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
