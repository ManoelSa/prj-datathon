from fastapi.testclient import TestClient
from app.main import app
from app import state
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest
import os

client = TestClient(app)


@pytest.fixture
def mock_model():
    """Mock do modelo sklearn/joblib"""
    mock = MagicMock()
    # Mock do predict_proba para retornar risco 0.7
    mock.predict_proba.return_value = pd.DataFrame([0.7]).values.reshape(1, -1) # Mock de array 1D/2D
    original_model = state.MODEL
    state.MODEL = mock
    yield mock
    state.MODEL = original_model

@pytest.fixture
def auth_header():

    username = os.getenv("APP_USER", "admin")
    password = os.getenv("APP_PASS", "admin")

    response = client.post("/token", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return {} 

@patch("app.router.log_prediction")
def test_predict_threshold_logic(mock_log, mock_model, auth_header):
    if not auth_header:
        pytest.skip("Auth não configurada")

    # Caso 1: Prob 0.7, Threshold 0.5 (Padrão) -> Deve ser 1 (Alto Risco)
    mock_model.predict_proba.return_value = pd.DataFrame([0.7]).values # 0.7 probabilidade
    
    payload = {
        "IAA": 5.0, "IEG": 5.0, "IPS": 5.0, "IDA": 5.0, 
        "IPP": 5.0, "IPV": 5.0, "IAN": 5.0, "INDE": 5.0, 
        "Defasagem": 0.0,
        "threshold": 0.5
    }
    
    response = client.post("/predict", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 1
    assert data["status"] == "Alto Risco"
    
    # Verifica se o log foi chamado
    mock_log.assert_called_once()

    # Caso 2: Prob 0.7, Threshold 0.8 -> Deve ser 0 (Baixo Risco)
    # Usuário é mais tolerante ao risco, só alerta se for > 80%
    payload["threshold"] = 0.8
    response = client.post("/predict", json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] == 0
    assert data["status"] == "Baixo Risco"

def test_predict_history(auth_header):
    if not auth_header:
        pytest.skip("Auth não configurada")
        
    response = client.get("/history?limit=5", headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    # Se houver dados, deve retornar no máximo 5
    assert len(response.json()) <= 5
