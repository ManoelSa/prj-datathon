import sys
from pathlib import Path
import os
import contextlib
import joblib
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram

# Adiciona a raiz do projeto ao sys.path para permitir o carregamento de módulos src do pickle
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# Importações após atualização do sys.path
from app import state
from app.router import router as prediction_router
from app.auth import Token, authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Define constantes
MODEL_PATH = os.path.join(PROJECT_ROOT, "app", "models", "risk_model.joblib")

# --- Métricas Prometheus ---
REQUEST_COUNT = Counter(
    "request_count", "Contagem de Requisições da App",
    ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "request_latency_seconds", "Latência das requisições",
    ["method", "endpoint"]
)

# Atribui ao state para acesso global se necessário
state.REQUEST_COUNT = REQUEST_COUNT
state.REQUEST_LATENCY = REQUEST_LATENCY


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de contexto Lifespan para carregar e descarregar recursos.
    """
    print("Iniciando API...")
    
    # Carregar Modelo
    if os.path.exists(MODEL_PATH):
        try:
            print(f"Carregando modelo de {MODEL_PATH}...")
            state.MODEL = joblib.load(MODEL_PATH)
            print("Modelo carregado com sucesso.")
        except Exception as e:
            print(f"ERRO: Falha ao carregar o modelo. {e}")
    else:
        print(f"AVISO: Arquivo do modelo não encontrado em {MODEL_PATH}")

    yield
    
    print("Desligando API...")
    state.MODEL = None


app = FastAPI(
    title="API de Previsão de Risco",
    description="API para previsão de risco estudantil usando Random Forest",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware ---
from datetime import datetime

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = datetime.now()
    method = request.method
    endpoint = request.url.path
    
    response = await call_next(request)
    
    # Não rastreia o endpoint de métricas para evitar ruído
    if endpoint != "/metrics":
        latency = (datetime.now() - start_time).total_seconds()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, http_status=response.status_code).inc()
        
    return response

# --- Rotas ---
app.include_router(prediction_router)

@app.post("/token", response_model=Token, tags=["Autenticação"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/", tags=["Saúde"])
def home():
    model_status = "Carregado" if state.MODEL else "Não Carregado"
    return {"message": "API de Previsão de Risco está Online", "model_status": model_status}

@app.get("/metrics", tags=["Monitoramento"])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
