import pandas as pd
import numpy as np
import re
from .config import INDICATOR_COLS

# Tabela Oficial de Fase Ideal por Idade (Baseado no Relatório PEDE 2022)
AGE_FASE_MAP = {
    6: 0, 7: 0, 8: 0,     # Alfa (Até 8 anos)
    9: 1,                 # Fase 1 (9 anos)
    10: 2, 11: 2,         # Fase 2 (10-11)
    12: 3, 13: 3,         # Fase 3 (12-13)
    14: 4,                # Fase 4 (14)
    15: 5,                # Fase 5 (15)
    16: 6,                # Fase 6 (16)
    17: 7,                # Fase 7 (17)
    18: 8, 19: 8, 20: 8,  # Fase 8 (18-20)
    21: 8, 22: 8, 23: 8, 24: 8 # Garantindo cobertura para universitários mais velhos
}

def get_fase_num(fase_val):
    """Extrai número da fase de string ou int."""
    if pd.isna(fase_val): return None
    s = str(fase_val).upper().strip()
    
    if 'ALFA' in s: return 0
    if 'FASE 8' in s or 'UNIVERSIT' in s: return 8
    
    # Procura dígito após "FASE" ou "Fase"
    match = re.search(r'FASE\s*(\d+)', s)
    if match: return int(match.group(1))
    
    # Se for apenas número ou começa com número (ex: "1A", "5B")
    digits = re.findall(r'\d+', s)
    if digits: return int(digits[0])
    
    return None

def calculate_corrected_defasagem(df):
    """
    Recalcula a defasagem baseada na Idade e Fase Real.
    D = Fase Real - Fase Ideal
    Resultado < 0 indica Atraso (Risco).
    """
    df_c = df.copy()
    
    # Identificar colunas (Normalização de nomes mais flexível)
    col_fase = next((c for c in df_c.columns if 'FASE' in c.upper() and 'IDEAL' not in c.upper()), None)
    col_idade = next((c for c in df_c.columns if 'IDADE' in c.upper()), None)
    col_ano = next((c for c in df_c.columns if 'ANO' in c.upper()), None)
    
    if not col_fase or not col_idade:
        # Se não tiver colunas para recalcular, retorna original se existir
        return df_c

    # Calcular
    def get_lag(row):
        try:
            val_idade = row[col_idade]
            idade = None
            
            # 1. Tenta extrair ano se for datetime (ex: data de nascimento)
            if hasattr(val_idade, 'year'):
                val_idade = val_idade.year
                
            # 2. Converte para int
            if pd.notnull(val_idade):
                 try:
                     idade = int(float(val_idade))
                 except:
                     idade = None
            
            # 3. Lógica de Ano de Nascimento (ex: > 1900)
            if idade and idade > 1900:
                # Tenta pegar o ano da base, se não tiver usa 2023 como fallback
                ano_atual = row.get(col_ano)
                if pd.isna(ano_atual): 
                    ano_atual = 2023 
                else:
                    ano_atual = int(float(ano_atual))
                    
                idade = ano_atual - idade
            
            # Se ainda assim a idade for inválida, fallback
            if idade is None: return row.get('Defasagem', None)
            
            # Pega Fase Ideal da tabela
            ideal = AGE_FASE_MAP.get(idade)
            if ideal is None:
                if idade > 18: ideal = 8
                elif idade < 6: ideal = 0
                else: return row.get('Defasagem', None) # Idade fora do range esperado
            
            real = get_fase_num(row[col_fase])
            if real is None: return row.get('Defasagem', None)
            
            # Cálculo: Real - Ideal
            # Ex: Fase 3 (Real) - Fase 4 (Ideal) = -1 (Atrasado)
            return real - ideal
            
        except Exception:
            return row.get('Defasagem', None)

    # Aplica correção
    df_c['Defasagem_Corrected'] = df_c.apply(get_lag, axis=1)
    
    # Substitui a coluna original pela calculada
    # Onde for NaN (falha no calculo), preenche com 0 (neutro) ou mantém original se existir
    original_defasagem = df_c.get('Defasagem', 0)
    df_c['Defasagem'] = df_c['Defasagem_Corrected'].fillna(original_defasagem)
    
    return df_c

def create_temporal_dataset(data_dict, year_t):
    """
    Cria um dataset temporal para treinamento supervisionado: Features (Ano T) -> Target (Ano T+1).
    """
    year_next = year_t + 1
    
    if year_t not in data_dict or year_next not in data_dict:
        print(f"Dados para transição {year_t} -> {year_next} não disponíveis.")
        return pd.DataFrame()
        
    df_t = data_dict[year_t].copy()
    df_next = data_dict[year_next].copy()
    
    # Recalcular Defasagem - Visto que no arquivo existem algumas inconsistencias de dados preenchida de forma supostamente equivocada.
    df_t = calculate_corrected_defasagem(df_t)
    df_next = calculate_corrected_defasagem(df_next)
    
    # Features de T
    # Garante que RA esteja presente
    cols_to_use = ['RA'] + [c for c in INDICATOR_COLS if c in df_t.columns]
    X = df_t[cols_to_use].copy()
    
    # Target de T+1 (Defasagem)
    if 'Defasagem' in df_next.columns:
        Y = df_next[['RA', 'Defasagem']].copy()
        Y.rename(columns={'Defasagem': 'Defasagem_Next'}, inplace=True)
        
        # Merge (Inner Join para pegar apenas alunos que continuaram)
        df_merged = pd.merge(X, Y, on='RA', how='inner')
        
        # Target: 1 se Defasagem_Next < 0 (Atrasado/Risco), caso contrário 0
        df_merged['Target_Risk'] = (df_merged['Defasagem_Next'] < 0).astype(int)
        
        return df_merged
    
    return pd.DataFrame()