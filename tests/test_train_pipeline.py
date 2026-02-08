import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.train_pipeline import main
from src.config import FEATURE_COLS

@patch('src.train_pipeline.load_data')
@patch('src.train_pipeline.create_temporal_dataset')
@patch('src.train_pipeline.TemporalPreprocessor')
@patch('src.train_pipeline.RiskModel')
@patch('src.train_pipeline.evaluate_model')
@patch('src.train_pipeline.print_reliability_report')
def test_train_pipeline_main_success(
    mock_print_report,
    mock_evaluate,
    mock_risk_model,
    mock_preprocessor,
    mock_create_temporal,
    mock_load_data
):
    # Configura mocks
    mock_load_data.return_value = {"dummy": "data"}
    
    # Cria DataFrame fictício
    df_data = {col: [1, 2, 3] for col in FEATURE_COLS}
    df_data['Target_Risk'] = [0, 1, 0]
    df = pd.DataFrame(df_data)
    
    # Retorna DataFrames não vazios para treino e teste
    mock_create_temporal.side_effect = [df, df]  # Primeira chamada para treino, segunda para teste
    
    # Mock da instância RiskModel
    mock_model_instance = MagicMock()
    mock_risk_model.return_value = mock_model_instance
    
    # Executa main
    with patch('src.train_pipeline.DATA_PATH') as mock_path:
        mock_path.exists.return_value = True
        main()
        
    # Asserções
    mock_load_data.assert_called_once()
    assert mock_create_temporal.call_count == 2
    mock_model_instance.train.assert_called_once()
    mock_model_instance.predict.assert_called_once()
    mock_model_instance.predict_proba.assert_called_once()
    mock_evaluate.assert_called_once()
    mock_print_report.assert_called_once()
    mock_model_instance.save.assert_called_once()

@patch('src.train_pipeline.DATA_PATH')
def test_train_pipeline_main_no_data(mock_data_path, capsys):
    mock_data_path.exists.return_value = False
    
    main()
    
    captured = capsys.readouterr()
    assert "Arquivo não encontrado" in captured.out

@patch('src.train_pipeline.load_data')
@patch('src.train_pipeline.create_temporal_dataset')
def test_train_pipeline_main_empty_datasets(mock_create_temporal, mock_load_data, capsys):
    # Configura mocks
    mock_load_data.return_value = {}
    
    # Retorna DataFrames vazios
    mock_create_temporal.return_value = pd.DataFrame()
    
    with patch('src.train_pipeline.DATA_PATH') as mock_path:
        mock_path.exists.return_value = True
        main()
        
    captured = capsys.readouterr()
    assert "Erro: Datasets vazios" in captured.out
