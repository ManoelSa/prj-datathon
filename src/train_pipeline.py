import sys
from pathlib import Path
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# sys.path hack removido - agora usamos pacote instalado
# SRC_DIR = Path(__file__).resolve().parent
# PROJECT_ROOT = SRC_DIR.parent
# sys.path.append(str(PROJECT_ROOT))

# Imports internos
from src.config import DATA_PATH, FEATURE_COLS, RANDOM_STATE, MODEL_PATH, MODELS_DIR
from src.data_loader import load_data
from src.feature_engineering import create_temporal_dataset
from src.preprocessing import TemporalPreprocessor
from src.modeling import RiskModel
from src.evaluation import evaluate_model, print_reliability_report

def main():
    # 1. Config basicas
    if not DATA_PATH.exists():
        print(f"Aviso: Arquivo não encontrado em {DATA_PATH}")
        return
    
    # 2. Carregando Dados
    print("Carregando dados...")
    data_dict = load_data(str(DATA_PATH))
    
    # 3. Engenharia de Features (Train: 22->23, Test: 23->24)
    print("Criando datasets temporais...")
    train_df = create_temporal_dataset(data_dict, 2022)
    test_df = create_temporal_dataset(data_dict, 2023)
    
    if train_df.empty or test_df.empty:
        print("Erro: Datasets vazios. Verifique seus dados.")
        return

    # 4. Seleção de features
    # Garantir colunas presentes
    train_cols = [c for c in FEATURE_COLS if c in train_df.columns]
    X_train = train_df[train_cols]
    y_train = train_df['Target_Risk']
    
    X_test = test_df[train_cols]
    y_test = test_df['Target_Risk']
    
    print(f"Treino: {X_train.shape}, Teste: {X_test.shape}")
    
    # 5. Construindo Pipeline
    print("Construindo Pipeline (Preprocessor + Model)...")
    
    pipeline = Pipeline([
        ('preprocessor', TemporalPreprocessor(feature_cols=train_cols)),
        ('clf', RandomForestClassifier(
            n_estimators=200, 
            max_depth=5, 
            class_weight='balanced', 
            random_state=RANDOM_STATE
        ))
    ])
    
    # 6. Treinando modelo
    print("Treinando modelo via Pipeline...")
    model = RiskModel(model=pipeline)
    model.train(X_train, y_train)
    
    # 7. Avaliação
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    metrics = evaluate_model(y_test, y_pred, y_prob)
    
    # Justificativa de Confiabilidade
    print_reliability_report(metrics)
    
    # 8. Salvando o modelo
    MODELS_DIR.mkdir(exist_ok=True)
    model.save(str(MODEL_PATH))
    
if __name__ == "__main__":
    main()
