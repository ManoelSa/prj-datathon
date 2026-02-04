import pandas as pd
import numpy as np
import pytest
from src.preprocessing import TemporalPreprocessor
from src.feature_engineering import create_temporal_dataset

@pytest.fixture
def mock_data_dict():
    """Cria dados fake para 2022 e 2023"""
    # 2022: 3 alunos
    df_22 = pd.DataFrame({
        'RA': ['1', '2', '3'],
        'IAA': [8.0, 9.0, np.nan], # Testar NaN
        'INDE': [7.0, 8.0, 6.0],
        'Defasagem': [0, 0, -1]
    })
    
    # 2023: Aluno 1 piorou, Aluno 2 sumiu, Aluno 3 manteve
    df_23 = pd.DataFrame({
        'RA': ['1', '3'], # Aluno 2 não existe em 2023
        'Defasagem': [-1, -1] # Ambos com risco
    })
    
    return {2022: df_22, 2023: df_23}

def test_temporal_dataset_merge(mock_data_dict):
    """Testa se o merge temporal (T -> T+1) funciona corretamente"""
    df_merged = create_temporal_dataset(mock_data_dict, 2022)
    
    # Deve ter 2 alunos (interseção de '1' e '3')
    assert len(df_merged) == 2
    assert 'Target_Risk' in df_merged.columns
    # Aluno 1: Defasagem_Next = -1 -> Target_Risk = 1
    assert df_merged.loc[df_merged['RA'] == '1', 'Target_Risk'].iloc[0] == 1

def test_temporal_dataset_missing_year():
    """Testa comportamento se o ano seguinte não existir"""
    data = {2022: pd.DataFrame()}
    df = create_temporal_dataset(data, 2022) # 2023 não existe
    assert df.empty

def test_preprocessor_imputation():
    """Testa se o preprocessor remove NaNs"""
    df = pd.DataFrame({
        'col1': [1.0, np.nan, 3.0],
        'col2': [np.nan, 5.0, 6.0]
    })
    
    prep = TemporalPreprocessor(feature_cols=['col1', 'col2'])
    transformed = prep.fit_transform(df)
    
    assert transformed.isnull().sum().sum() == 0
    assert transformed.iloc[1, 0] == 2.0 # Mediana de col1 (1, 3 -> 2)

def test_preprocessor_auto_columns():
    """Testa se o preprocessor detecta colunas automaticamente se feature_cols=None"""
    df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    prep = TemporalPreprocessor(feature_cols=None)
    prep.fit(df)
    
    assert prep.feature_cols == ['col1', 'col2']
    
def test_temporal_dataset_missing_target_col(mock_data_dict):
    """Testa se retorna vazio caso a coluna 'Defasagem' não exista no ano T+1"""
    # Remove coluna Defasagem de 2023
    del mock_data_dict[2023]['Defasagem']
    
    df = create_temporal_dataset(mock_data_dict, 2022)
    assert df.empty
