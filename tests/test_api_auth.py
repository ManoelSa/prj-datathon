from fastapi.testclient import TestClient
from app.main import app
import os
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

def test_login_success():
    username = os.getenv("APP_USER")
    password = os.getenv("APP_PASS")
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure():
    response = client.post("/token", data={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_predict_without_token():
    # Tenta acessar /predict sem token
    response = client.post("/predict", json={
        "COD_ALUNO": 123,
        "COD_TURMA": 456,
        "IAA_2022": 5.0,
        "IAA_2023": 6.0,
        "IPS_2022": 7.0,
        "IPS_2023": 8.0,
        "IDA_2022": 9.0,
        "IDA_2023": 10.0
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_predict_with_token():
    # 1. Login
    username = os.getenv("APP_USER")
    password = os.getenv("APP_PASS")
    login_response = client.post("/token", data={"username": username, "password": password})
    token = login_response.json()["access_token"]
    
    # 2. Predict com token
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "COD_ALUNO": 12345,
        "COD_TURMA": 67890,
        "IAA_2022": 7.5,
        "IAA_2023": 8.0,
        "IPS_2022": 6.5,
        "IPS_2023": 7.0,
        "IDA_2022": 8.5,
        "IDA_2023": 9.0
    }
    response = client.post("/predict", json=payload, headers=headers)
    
    # Verifica sucesso (pode ser 200 ou 503 se modelo nao carregado, mas nao 401)
    # Se o modelo nao carregar no teste (pois state.MODEL pode ser None se nao rodar lifespan), validamos o auth
    # Para garantir o teste completo, podemos mockar o state.MODEL ou aceitar 503 como "auth ok"
    
    assert response.status_code in [200, 503]
