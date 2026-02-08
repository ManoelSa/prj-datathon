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
            '1': {'precision': 0.75}
        }
    }
    
    print_reliability_report(metrics)
    
    captured = capsys.readouterr()
    assert "Métrica Principal (ROC AUC): 0.8500" in captured.out
    assert "Precision de 0.75" in captured.out
