from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from app import state
from app.auth import get_current_user
from app.schemas import PredictionInput, PredictionOutput
import csv
import os
from datetime import datetime

router = APIRouter()

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
        # --- 1. INFERÊNCIA OTIMIZADA ---
        # Calculamos APENAS a probabilidade, pois a classe final será decidida 
        # dinamicamente com base no threshold do usuário.
                
        prob_raw = state.MODEL.predict_proba(df)
        
        # Extração segura do valor float (compatível com array 1D ou 2D)
        probability_value = prob_raw.flatten()[0]
        if hasattr(probability_value, "item"):
            probability_value = probability_value.item()

        # --- 2. Define a predição final baseada no limiar (threshold) escolhido pelo usuário.
        # Se probabilidade >= threshold -> Alto Risco (1)
        # Caso contrário -> Baixo Risco (0)
        prediction_final = 1 if probability_value >= data.threshold else 0
        
        status = "Alto Risco" if prediction_final == 1 else "Baixo Risco"

        # --- 3. LOGGING COMPLETO (Input + Output) ---
        # Salva o histórico para monitoramento futuro de Data Drift e Concept Drift.
            
        LOG_FILE = "data/production_logs.csv"
        os.makedirs("data", exist_ok=True)
        
        # Prepara o registro completo
        log_entry = input_data.copy()
        log_entry["timestamp"] = datetime.now().isoformat()
        log_entry["prediction"] = prediction_final  # O que foi decidido de fato
        log_entry["probability"] = probability_value # A certeza do modelo
        log_entry["status"] = status
        
        # Escreve no CSV (Modo Append)  << No futuro trocar todo este processo para banco de dados >> 
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
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
def get_prediction_history():
    """Lê o arquivo de logs e retorna como JSON."""
    LOG_FILE = "data/production_logs.csv"
    import os
    if not os.path.exists(LOG_FILE):
        return []
    
    try:
        df = pd.read_csv(LOG_FILE)
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao ler histórico: {str(e)}")
