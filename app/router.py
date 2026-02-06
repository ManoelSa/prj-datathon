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
