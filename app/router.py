from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from app import state
from app.auth import get_current_user
from app.schemas import PredictionInput, PredictionOutput
import csv
import os
from datetime import datetime
import json
import time

router = APIRouter()


# Escreve no CSV (Modo Append) << No futuro trocar todo este processo para banco de dados >>
def log_prediction(log_entry: dict):
    """Salva a predição no arquivo de logs (CSV)."""
    LOG_FILE = "data/production_logs.csv"
    os.makedirs("data", exist_ok=True)
    
    file_exists = os.path.isfile(LOG_FILE)
    
    # Verifica Schema Evolution (Se adicionarmos novos campos como latency_ms)
    if file_exists:
        try:
            with open(LOG_FILE, 'r', newline='', encoding='utf-8') as f:
                header = next(csv.reader(f), None)
            
            if header:
                existing_keys = set(header)
                new_keys = set(log_entry.keys())
                missing_in_file = new_keys - existing_keys
                
                if missing_in_file:
                    # Reescreve com as novas colunas
                    df_temp = pd.read_csv(LOG_FILE)
                    for k in missing_in_file:
                        df_temp[k] = None # Preenche passados com vazio
                    df_temp.to_csv(LOG_FILE, index=False)
        except Exception:
            pass # Se falhar a migração, tenta append normal

    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if not file_exists or os.path.getsize(LOG_FILE) == 0:
            writer.writeheader()
        writer.writerow(log_entry)

@router.post("/predict", 
    response_model=PredictionOutput, 
    dependencies=[Depends(get_current_user)],
    tags=["Predição"],
    summary="Previsão de Risco Acadêmico"
)
def predict(data: PredictionInput):
    """
    Processa indicadores educacionais (IAA, IEG, IPS, etc.) para calcular a probabilidade de risco de evasão do aluno.

    Endpoint para inferência do modelo de Machine Learning.
    
    - **IAA**: Índice de Autoavaliação da Aprendizagem
    - **IEG**: Índice de Engajamento Geral
    - **IPS**: Índice Psicossocial
    - **IDA**: Índice de Dificuldade de Aprendizagem
    - **IPP**: Índice de Prática Pedagógica
    - **PV**: Índice de Ponto de Virada
    - **IAN**: Índice de Adequação de Nível
    - **INDE**: Índice de Desenvolvimento Educacional
    - **Defasagem**: Nível de defasagem escolar
    """
    if state.MODEL is None:
        raise HTTPException(status_code=503, detail="Modelo não carregado")

    # Converte os dados de entrada para DataFrame (formato esperado pelo modelo)
    input_data = data.model_dump()
    df = pd.DataFrame([input_data])
    
    try:
        # --- 1. INFERÊNCIA ---
        start_time = time.perf_counter() # Início da medição de latência
        
        # Calculamos APENAS a probabilidade, pois a classe final será decidida 
        # dinamicamente com base no threshold do usuário.
                
        prob_raw = state.MODEL.predict_proba(df)
        
        probability_value = prob_raw.flatten()[0]
        if hasattr(probability_value, "item"):
            probability_value = probability_value.item()

        # --- 2. Define a predição final baseada no limiar (threshold) escolhido pelo usuário.
        # Se probabilidade >= threshold -> Alto Risco (1)
        # Caso contrário -> Baixo Risco (0)
        prediction_final = 1 if probability_value >= data.threshold else 0
        
        status = "Alto Risco" if prediction_final == 1 else "Baixo Risco"
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000 # Converte para milissegundos

        # --- 3. LOGGING COMPLETO (Input + Output) ---
        # Salva o histórico para monitoramento futuro de Data Drift e performance da API << No futuro trocar todo este processo para banco de dados >>.
        try:
            # Prepara o registro
            log_entry = input_data.copy()
            log_entry["timestamp"] = datetime.now().isoformat()
            log_entry["prediction"] = prediction_final
            log_entry["probability"] = probability_value
            log_entry["status"] = status
            log_entry["latency_ms"] = round(latency_ms, 2)
            
            log_prediction(log_entry)
        except Exception as e:
            # Não falha a requisição se o log falhar, apenas imprime erro no console
            print(f"Erro ao salvar log: {e}")
        # --- FIM DO LOGGING ---

        # Retorna o resultado estruturado
        return PredictionOutput(
            prediction=int(prediction_final), 
            probability=float(probability_value),
            status=status
        )

    except Exception as e:
        # Em caso de erro, retorna 500 com detalhes para debug
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@router.get("/history",
    dependencies=[Depends(get_current_user)],
    tags=["Monitoramento"],
    summary="Histórico de Predições",
    description="Retorna os dados de entrada das últimas predições para análise de Drift."
)
def get_prediction_history(limit: int = 100):
    """
    Lê o arquivo de logs e retorna como JSON.
    Args:
        limit (int): Número máximo de registros para retornar (padrão: 100). 
                     Use 0 para retornar todo o histórico.
    """
    LOG_FILE = "data/production_logs.csv"
    import os
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        # Leitura otimizada: ler tudo mas retornar apenas os últimos 'limit'
        # Futuro migrar para BANCO de DADOS
        df = pd.read_csv(LOG_FILE)
        
        # Pega os últimos N registros (Se limit > 0)
        # Se limit <= 0, retorna TUDO.
        if limit > 0:
            df_limited = df.tail(limit)
        else:
            df_limited = df
        
        # Ordena do mais recente para o mais antigo
        df_limited = df_limited[::-1]
        
        return json.loads(df_limited.to_json(orient="records"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler histórico: {str(e)}")
