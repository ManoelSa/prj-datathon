import pandas as pd
from .config import INDICATOR_COLS

def create_temporal_dataset(data_dict, year_t):
    """
    Cria um dataset temporal para treinamento supervisionado: Features (Ano T) -> Target (Ano T+1).
    Args:
        data_dict (dict): Dicionário com DataFrames por ano.
        year_t (int): Ano base das features.
    Returns:
        pd.DataFrame: DataFrame com features de T e target de T+1.
    """
    year_next = year_t + 1
    
    if year_t not in data_dict or year_next not in data_dict:
        print(f"Dados para {year_t} ou {year_next} não disponíveis.")
        return pd.DataFrame()
        
    df_t = data_dict[year_t]
    df_next = data_dict[year_next]
    
    # Features de T
    features_t = ['RA'] + INDICATOR_COLS
    features_t = [f for f in features_t if f in df_t.columns]
    X = df_t[features_t].copy()
    
    # Target de T+1 (Defasagem)
    if 'Defasagem' in df_next.columns:
        Y = df_next[['RA', 'Defasagem']].copy()
        Y.rename(columns={'Defasagem': 'Defasagem_Next'}, inplace=True)
        
        # Merge
        df_merged = pd.merge(X, Y, on='RA', how='inner')
        
        # Target: 1 se Defasagem_Next < 0 (Risco), else 0
        df_merged['Target_Risk'] = (df_merged['Defasagem_Next'] < 0).astype(int)
        
        return df_merged
    
    return pd.DataFrame()
