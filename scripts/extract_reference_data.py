import pandas as pd
import os

# Configurações
EXCEL_PATH = "BASE DE DADOS PEDE 2024 - DATATHON.xlsx"
OUTPUT_PATH = "data/reference_data.csv"
FEATURE_COLS = ["IAA", "IEG", "IPS", "IDA", "IPP", "IPV", "IAN", "INDE", "Defasagem"]

def main():
    if not os.path.exists(EXCEL_PATH):
        print(f"Erro: Arquivo {EXCEL_PATH} não encontrado.")
        return

    print("Carregando Excel base de dados...")
    dfs = []
    
    # Mapeamento explícito de colunas por ano
    # Sintaxe: { 'Coluna_Original': 'Coluna_Destino' }
    YEAR_MAPS = {
        "PEDE 2022": {
            "IAA": "IAA", "IEG": "IEG", "IPS": "IPS", "IDA": "IDA", 
            "IPP": "IPP", "IPV": "IPV", "IAN": "IAN", 
            "INDE 22": "INDE", "Defas": "Defasagem"
        },
        "PEDE 2023": {
            "IAA": "IAA", "IEG": "IEG", "IPS": "IPS", "IDA": "IDA", 
            "IPP": "IPP", "IPV": "IPV", "IAN": "IAN", 
            "INDE 2023": "INDE", "Defasagem": "Defasagem"
        }
        # FUTURO: Quando tiver o modelo treinado com 2024, adicione:
        # "PEDE 2024": { ... }
    }

    # Carrega APENAS dados históricos conhecidos pelo modelo
    # NOTA: Atualize esta lista quando re-treinar o modelo com novos anos!
    for year_sheet, col_map in YEAR_MAPS.items():
        try:
            print(f"Lendo aba {year_sheet} (Histórico)...")
            # Tenta ler com nome sem espaço primeiro (padrão do código original)
            try:
               d = pd.read_excel(EXCEL_PATH, sheet_name=year_sheet.replace(" ", ""))
            except:
               d = pd.read_excel(EXCEL_PATH, sheet_name=year_sheet)

            # Filtra apenas colunas existentes e renomeia
            valid_cols = [c for c in col_map.keys() if c in d.columns]
            d = d[valid_cols].rename(columns=col_map)
            
            # Adiciona coluna de ano para referência
            d["Ano"] = int(year_sheet.split(" ")[1])
            
            dfs.append(d)
        except Exception as e:
            print(f"Erro ao ler aba {year_sheet}: {e}")
            
    if not dfs:
        print("Nenhuma aba histórica encontrada! Verifique o arquivo.")
        return
        
    df = pd.concat(dfs, ignore_index=True)
    
    # Filtra colunas
    available_cols = [c for c in FEATURE_COLS if c in df.columns]
    
    if not available_cols:
        print("Nenhuma coluna de feature encontrada!")
        print("Colunas disponíveis:", df.columns.tolist())
        return
        
    df_ref = df[available_cols].dropna()
    
    # Cria diretório se não existir
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    # Salva CSV
    df_ref.to_csv(OUTPUT_PATH, index=False)
    print(f"Sucesso! Dados de referência extraídos para {OUTPUT_PATH}")
    print(f"Linhas: {len(df_ref)}")

if __name__ == "__main__":
    main()
