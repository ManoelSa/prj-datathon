import pandas as pd
import numpy as np
import os

def load_data(file_path):
    """
    Carrega dados de múltiplas abas de um arquivo Excel e padroniza os DataFrames.

    Lê as abas correspondentes aos anos de 2022, 2023 e 2024, realiza a renomeação de colunas
    para um padrão comum e aplica limpeza inicial em colunas numéricas.

    Args:
        file_path (str): Caminho absoluto ou relativo para o arquivo Excel (.xlsx).

    Returns:
        dict: Um dicionário onde as chaves são os anos (int) e os valores são os DataFrames (pd.DataFrame) carregados e tratados.
              Exemplo: {2022: df_22, 2023: df_23, ...}
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
    xls = pd.ExcelFile(file_path)
    data = {}
    
    # --- 2022 ---
    if 'PEDE2022' in xls.sheet_names:
        df = pd.read_excel(xls, 'PEDE2022')
        df.rename(columns={
            'INDE 22': 'INDE', 'Defas': 'Defasagem', 
            'IAA': 'IAA', 'IEG': 'IEG', 'IPS': 'IPS', 'IDA': 'IDA', 'IPV': 'IPV', 'IAN': 'IAN'
        }, inplace=True)
        df = _clean_numeric_cols(df)
        df['RA'] = df['RA'].astype(str).str.strip()
        df['Ano'] = 2022
        data[2022] = df
        
    # --- 2023 ---
    if 'PEDE2023' in xls.sheet_names:
        df = pd.read_excel(xls, 'PEDE2023')
        df.rename(columns={'INDE 2023': 'INDE'}, inplace=True)
        df = _clean_numeric_cols(df)
        df['RA'] = df['RA'].astype(str).str.strip()
        df['Ano'] = 2023
        data[2023] = df

    # --- 2024 ---
    if 'PEDE2024' in xls.sheet_names:
        df = pd.read_excel(xls, 'PEDE2024')
        df.rename(columns={'INDE 2024': 'INDE'}, inplace=True)
        df = _clean_numeric_cols(df)
        df['RA'] = df['RA'].astype(str).str.strip()
        df['Ano'] = 2024
        data[2024] = df
        
    return data

def _clean_numeric_cols(df):
    """
    Converte colunas de indicadores para tipo numérico, forçando erros a NaN.

    Esta função auxiliar percorre uma lista pré-definida de colunas de indicadores educacionais
    e tenta convertê-las para float. Valores não numéricos (como texto ou vazios) são substituídos por NaN.

    Args:
        df (pd.DataFrame): O DataFrame contendo os dados brutos.

    Returns:
        pd.DataFrame: O DataFrame com as colunas de indicadores devidamente convertidas para numérico.
    """
    cols_to_clean = ['IAA', 'IEG', 'IPS', 'IDA', 'IPV', 'IPP', 'IAN', 'INDE', 'Defasagem']
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df
