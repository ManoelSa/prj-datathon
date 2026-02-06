
import pandas as pd
import pytest
import os
from src.data_loader import load_data, _clean_numeric_cols

@pytest.fixture
def mock_excel_file(tmp_path):
    """Cria um arquivo Excel temporário para teste"""
    # Dados Fake
    df_22 = pd.DataFrame({'RA': ['1', '2'], 'INDE 22': [7, 8], 'IAA': ['8.0', 'text']}) # 'text' vira NaN
    df_23 = pd.DataFrame({'RA': ['1', '2'], 'INDE 2023': [8, 9]})
    df_24 = pd.DataFrame({'RA': ['1', '2'], 'INDE 2024': [9, 9]})
    
    # Salvar em Excel
    file_path = tmp_path / "test_db.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        df_22.to_excel(writer, sheet_name='PEDE2022', index=False)
        df_23.to_excel(writer, sheet_name='PEDE2023', index=False)
        df_24.to_excel(writer, sheet_name='PEDE2024', index=False)
        
    return str(file_path)

def test_load_data_success(mock_excel_file):
    """Testa leitura Funcional"""
    data_dict = load_data(mock_excel_file)
    
    assert 2022 in data_dict
    assert 2023 in data_dict
    assert 2024 in data_dict
    assert len(data_dict[2022]) == 2
    # Verifica padronização de nomes
    assert 'INDE' in data_dict[2022].columns
    
def test_load_data_numeric_cleaning(mock_excel_file):
    """Testa se string vira NaN na limpeza"""
    data_dict = load_data(mock_excel_file)
    df_22 = data_dict[2022]
    
    # Linha 2 do IAA era 'text', deve virar NaN
    assert pd.isna(df_22['IAA'].iloc[1])

def test_file_not_found():
    """Testa erro se arquivo não existe"""
    with pytest.raises(FileNotFoundError):
        load_data("arquivo_inexistente.xlsx")
