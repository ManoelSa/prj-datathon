import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

API_URL = "http://localhost:8000" 
USERNAME = os.getenv("APP_USER", "admin") # Ajuste se necessário
PASSWORD = os.getenv("APP_PASS", "admin") # Ajuste se necessário

def login():
    try:
        response = requests.post(
            f"{API_URL}/token",
            data={"username": USERNAME, "password": PASSWORD},
            timeout=5
        )
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Falha no login: {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao conectar para login: {e}")
        return None

def predict_2024():
    print("--- Autenticando ---")
    token = login()
    if not token:
        print("Abortando: Não foi possível obter token.")
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("--- Carregando dados de 2024 ---")
    file_path = 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx'
    
    try:
        df = pd.read_excel(file_path, sheet_name='PEDE2024')
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return
    
    # Renomeia INDE 2024 -> INDE (Ajuste de nome)
    if 'INDE 2024' in df.columns:
        df.rename(columns={'INDE 2024': 'INDE'}, inplace=True)
    
    # Lista de colunas que a API espera
    features = ['IAA', 'IEG', 'IPS', 'IDA', 'IPP', 'IPV', 'IAN', 'INDE', 'Defasagem']
    
    missing_cols = [c for c in features if c not in df.columns]
    
    if missing_cols:
        print(f"Colunas faltando no Excel: {missing_cols}")
        print("Criando colunas com valor NULL para o Backend usar a Mediana...")
        for c in missing_cols:
            df[c] = None
            
    # --- CORREÇÃO DE DEFASAGEM (Regra de Idade) ---
    print("Aplicando Correção de Defasagem (Idade -> Fase Ideal)...")
    import re
    AGE_FASE_MAP = {
        7: 0, 8: 0, 9: 1, 10: 2, 11: 2, 12: 3, 13: 3, 14: 4, 
        15: 5, 16: 6, 17: 7, 18: 8, 19: 8, 20: 8
    }
    
    def get_corrected_defasagem(row):
        try:
            val_idade = row.get('IDADE') or row.get('Idade')
            val_fase = row.get('FASE') or row.get('Fase')
            
            if pd.isna(val_idade) or pd.isna(val_fase): return row.get('Defasagem')
            
            idade = None
            # 1. Tenta extrair ano se for datetime
            if hasattr(val_idade, 'year'):
                val_idade = val_idade.year
                
            # 2. Converte para int
            if pd.notnull(val_idade):
                 try:
                     idade = int(val_idade)
                 except:
                     idade = None
            
            # 3. Se for Ano de Nascimento (ex: > 1900), converter para Idade (Base 2024 -> Ano Ref 2024)
            if idade and idade > 1900:
                idade = 2024 - idade
            
            target_ideal = AGE_FASE_MAP.get(idade)
            if target_ideal is None: 
                if idade > 18: target_ideal = 8
                elif idade < 7: target_ideal = 0
                else: return row.get('Defasagem')

            s_fase = str(val_fase).upper()
            real = None
            if 'ALFA' in s_fase: real = 0
            else:
                match = re.search(r'FASE\s*(\d+)', s_fase)
                if match: real = int(match.group(1))
                else: 
                    digs = re.findall(r'\d+', s_fase)
                    if digs: real = int(digs[0])
            
            if real is not None:
                return real - target_ideal
            return row.get('Defasagem')
        except:
            return row.get('Defasagem')

    df['Defasagem_Corrigida'] = df.apply(get_corrected_defasagem, axis=1)
    if 'Defasagem' in df.columns:
        df['Defasagem'] = df['Defasagem_Corrigida'].fillna(df['Defasagem'])
    else:
        df['Defasagem'] = df['Defasagem_Corrigida']

    # Cria o DataFrame apenas com as colunas necessárias
    df_pred = df[features].copy()
    
    # Garante que os dados sejam numéricos, transformando erros em NaN
    for col in features:
        df_pred[col] = pd.to_numeric(df_pred[col], errors='coerce')
        
    # Converte para tipo 'object' para aceitar None
    df_pred = df_pred.astype(object)
    
    # Substitui NaN (do Pandas) por None (do Python) para virar 'null' no JSON
    df_pred = df_pred.where(pd.notnull(df_pred), None)
    
    results = []
    
    print(f"--- Iniciando Predições para {len(df_pred)} alunos ---")
    
    total = len(df_pred)
    start_time = time.time()
    
    for idx, row in df_pred.iterrows():
        # Feedback visual a cada 50 registros
        if idx % 50 == 0:
            print(f"Processando registro {idx}/{total}...")
            
        payload = row.to_dict()
        
        try:
            # Envia para a API
            response = requests.post(f"{API_URL}/predict", json=payload, headers=headers, timeout=30)
            
            # Tenta recuperar o RA para salvar no resultado (se existir no original)
            ra_aluno = df.loc[idx, 'RA'] if 'RA' in df.columns else idx
            
            if response.status_code == 200:
                data = response.json()
                results.append({
                    "RA": ra_aluno,
                    "Prediction": data.get("prediction"),
                    "Probability": data.get("probability"),
                    "Status": data.get("status")
                })
            else:
                # Erro de negócio ou validação (ex: 422, 500)
                results.append({
                    "RA": ra_aluno,
                    "Prediction": -1,
                    "Probability": -1,
                    "Status": f"Erro API: {response.status_code}"
                })
                
        except Exception as e:
                # Erro de conexão (timeout, servidor fora)
                ra_aluno = df.loc[idx, 'RA'] if 'RA' in df.columns else idx
                results.append({
                    "RA": ra_aluno,
                    "Prediction": -1,
                    "Probability": -1,
                    "Status": f"Erro Conexão: {str(e)}"
                })
    
    end_time = time.time()
    print(f"Tempo total: {end_time - start_time:.2f}s")
    
    # Salva os resultados em CSV
    df_results = pd.DataFrame(results)
    output_file = "predictions_2024.csv"
    df_results.to_csv(output_file, index=False)
    
    print(f"\n--- Concluído ---")
    print(f"Resultados salvos em {output_file}")
    
    if 'Status' in df_results.columns:
        print("\nResumo dos Status:")
        print(df_results['Status'].value_counts())

if __name__ == "__main__":
    predict_2024()