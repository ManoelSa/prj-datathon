import pandas as pd
import pytest
from src.feature_engineering import calculate_corrected_defasagem, get_fase_num

def test_get_fase_num():
    assert get_fase_num("Fase 1") == 1
    assert get_fase_num("2 Fase") == 2
    assert get_fase_num("Fase 4B") == 4
    assert get_fase_num("Alfa") == 0
    assert get_fase_num("Fase 8") == 8
    assert get_fase_num("Universitário") == 8
    assert get_fase_num(None) is None

def test_correction_logic():
    # Cenário 1: Idade 14, Fase 4 (Ideal) -> Defasagem 0
    df = pd.DataFrame({
        'RA': [1],
        'Idade': [14],
        'Fase': ['Fase 4'],
        'Defasagem': [99] # Valor errado original
    })
    
    df_new = calculate_corrected_defasagem(df)
    assert df_new.iloc[0]['Defasagem'] == 0.0

    # Cenário 2: Idade 14, Fase 3 (Atrasado) -> Defasagem -1
    df = pd.DataFrame({
        'RA': [2],
        'Idade': [14],
        'Fase': ['Fase 3'],
        'Defasagem': [0]
    })
    df_new = calculate_corrected_defasagem(df)
    assert df_new.iloc[0]['Defasagem'] == -1.0

def test_age_cleaning_logic():
    # Cenário 3: Idade como Ano de Nascimento (2010), Base 2023 -> Idade 13
    # 2023 - 2010 = 13 anos -> Fase Ideal 3 (para 12-13)
    # Se Fase Real 3 -> Defasagem 0
    
    df = pd.DataFrame({
        'RA': [3],
        'Idade': [2010],
        'Fase': ['Fase 3'],
        'ANO': [2023],
        'Defasagem': [0]
    })
    
    df_new = calculate_corrected_defasagem(df)
    
    # 13 anos -> Fase Ideal 3. Fase Real 3. Defasagem 0.
    assert df_new.iloc[0]['Defasagem'] == 0.0
