import os
from pathlib import Path

# Paths
SRC_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SRC_DIR.parent
DATA_PATH = PROJECT_ROOT / 'BASE DE DADOS PEDE 2024 - DATATHON.xlsx'
MODELS_DIR = PROJECT_ROOT / 'app/models'

# Model Configuration
MODEL_FILENAME = 'risk_model.joblib'
MODEL_PATH = MODELS_DIR / MODEL_FILENAME

# Columns
INDICATOR_COLS = ['IAA', 'IEG', 'IPS', 'IDA', 'IPP', 'IPV', 'IAN', 'INDE', 'Defasagem']
FEATURE_COLS = ['IAA', 'IEG', 'IPS', 'IDA', 'IPP', 'IPV', 'IAN', 'INDE', 'Defasagem']

# Random State
RANDOM_STATE = 42

# Configuração do Modelo
MODEL_TYPE = 'random_forest' # Opções: 'random_forest', 'logistic_regression', 'gradient_boosting'

MODEL_HYPERPARAMETERS = {
    'random_forest': {
        'n_estimators': 200,
        'max_depth': 5,
        'class_weight': 'balanced',
        'random_state': RANDOM_STATE
    },
    'logistic_regression': {
        'C': 1.0,
        'penalty': 'l2',
        'solver': 'lbfgs',
        'class_weight': 'balanced',
        'max_iter': 1000,
        'random_state': RANDOM_STATE
    },
    'gradient_boosting': {        
        'learning_rate': 0.1,
        'max_iter': 200,          
        'max_depth': 3,
        'class_weight': 'balanced', 
        'random_state': RANDOM_STATE,
        'scoring': 'loss',        
        'validation_fraction': 0.1,
        'n_iter_no_change': 10
    }
}