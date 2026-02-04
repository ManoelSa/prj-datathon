
import pandas as pd
import numpy as np
import pytest
import os
from src.modeling import RiskModel
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

@pytest.fixture
def sample_data():
    X = pd.DataFrame(np.random.rand(10, 5), columns=[f'col_{i}' for i in range(5)])
    y = pd.Series(np.random.randint(0, 2, 10))
    return X, y

def test_risk_model_training(sample_data):
    X, y = sample_data
    model = RiskModel(n_estimators=10)
    model.train(X, y)
    
    assert model.feature_cols == list(X.columns)
    
def test_risk_model_prediction(sample_data):
    X, y = sample_data
    model = RiskModel(n_estimators=10)
    model.train(X, y)
    
    preds = model.predict(X)
    probs = model.predict_proba(X)
    
    assert len(preds) == len(X)
    assert len(probs) == len(X)
    assert set(preds).issubset({0, 1}) # Só classes 0 e 1

def test_risk_model_with_pipeline(sample_data):
    """Testa se RiskModel aceita um Pipeline injetado"""
    X, y = sample_data
    
    pipeline = Pipeline([
        ('clf', RandomForestClassifier(n_estimators=10))
    ])
    
    model = RiskModel(model=pipeline)
    model.train(X, y)
    
    # Verifica se o treino funcionou chamando predict
    preds = model.predict(X)
    assert len(preds) == 10

def test_risk_model_save_load(sample_data, tmp_path):
    X, y = sample_data
    model = RiskModel(n_estimators=5)
    model.train(X, y)
    
    save_path = tmp_path / "test_model.pkl"
    model.save(str(save_path))
    
    assert os.path.exists(save_path)
    
    # Load em nova instância
    new_model = RiskModel()
    new_model.load(str(save_path))
    
    # Previsões devem ser iguais
    assert np.array_equal(model.predict(X), new_model.predict(X))

