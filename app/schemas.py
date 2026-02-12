from pydantic import BaseModel, Field, ConfigDict

class PredictionInput(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "IAA": 5.5,
            "IEG": 6.2,
            "IPS": 7.0,
            "IDA": 8.0,
            "IPP": 4.5,
            "IPV": 6.1,
            "IAN": 5.0,
            "INDE": 6.5,
            "Defasagem": 0.0
        }
    })

    IAA: float = Field(..., description="Índice de Autoavaliação da Aprendizagem")
    IEG: float = Field(..., description="Índice de Engajamento Geral")
    IPS: float = Field(..., description="Índice Psicossocial")
    IDA: float = Field(..., description="Índice de Dificuldade de Aprendizagem")
    IPP: float = Field(..., description="Índice de Prática Pedagógica")
    IPV: float = Field(..., description="Índice de Ponto de Virada")
    IAN: float = Field(..., description="Índice de Adequação de Nível")
    INDE: float = Field(..., description="Índice de Desenvolvimento Educacional")
    Defasagem: float = Field(..., description="Defasagem Escolar")
    threshold: float = Field(0.5, description="Limiar de Risco (0.0 a 1.0)", ge=0.0, le=1.0)

class PredictionOutput(BaseModel):
    prediction: int = Field(..., description="Predição de Risco (0 ou 1)")
    probability: float = Field(..., description="Probabilidade de Risco")
    status: str = Field(..., description="Status de Risco (Ex: Baixo Risco, Alto Risco)")
