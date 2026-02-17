import pytest
import pandas as pd
import numpy as np
from src.evaluation import evaluate_model, print_reliability_report

def test_evaluate_model_metrics():
    # Configura dados fictícios
    y_test = pd.Series([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0])  # Um falso negativo
    y_prob = np.array([0.1, 0.9, 0.2, 0.4])
    
    metrics = evaluate_model(y_test, y_pred, y_prob)
    
    # Verifica estrutura
    assert 'auc' in metrics
    assert 'report' in metrics
    
    # Verifica valores
    assert isinstance(metrics['auc'], float)
    assert 0 <= metrics['auc'] <= 1
    
    report = metrics['report']
    assert 'accuracy' in report
    assert '1' in report  # Classe de Risco
    assert '0' in report  # Classe de Não-Risco

def test_print_reliability_report(capsys):
    metrics = {
        'auc': 0.85,
        'report': {
            '1': {'precision': 0.75, 'recall': 0.80}
        }
    }
    
    print_reliability_report(metrics)
    
    captured = capsys.readouterr()
    # Verifica se a nova mensagem focada em Recall está presente
    assert "Relatório de Confiabilidade do Modelo SAPE" in captured.out
    assert "Métrica Principal de Decisão: Recall" in captured.out
    assert "80.00%" in captured.out
    assert "Robustez Geral (ROC AUC 0.85)" in captured.out
