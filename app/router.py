from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
from app import state
from app.auth import get_current_user
from app.schemas import PredictionInput, PredictionOutput

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

    # Converte para DataFrame
    input_data = data.model_dump()
    df = pd.DataFrame([input_data])
    
    try:
        # --- LOGGING INIT ---
        # Salva o input no historico de produção (CSV local)
        # A ideia é implementar um banco de dados para produção real/futuro
        import csv
        import os
        from datetime import datetime
        
        LOG_FILE = "data/production_logs.csv"
        os.makedirs("data", exist_ok=True)
        
        # Adiciona timestamp
        log_entry = input_data.copy()
        log_entry["timestamp"] = datetime.now().isoformat()
        
        # Escreve no CSV (Append mode)
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(log_entry)
        # --- LOGGING END ---

        # Realiza a predição
        # Passando features brutas para o pipeline que lida com o pré-processamento
        pred_raw = state.MODEL.predict(df)
        prob_raw = state.MODEL.predict_proba(df)
        
        # Pega o primeiro elemento (suporta tanto array 1D quanto 2D)
        prediction_value = pred_raw.flatten()[0]
        probability_value = prob_raw.flatten()[0]
        
        # Conversão robusta para tipos nativos do Python
        if hasattr(prediction_value, "item"):
            prediction_value = prediction_value.item()
            
        if hasattr(probability_value, "item"):
            probability_value = probability_value.item()

        return PredictionOutput(prediction=int(prediction_value), probability=float(probability_value))
    except Exception as e:
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
