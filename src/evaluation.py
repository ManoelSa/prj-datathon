from sklearn.metrics import classification_report, roc_auc_score

def evaluate_model(y_test, y_pred, y_prob):
    """
    Calcula e imprime métricas de avaliação do modelo.
    Args:
        y_test (pd.Series): Valores reais.
        y_pred (np.array): Predições de classe.
        y_prob (np.array): Probabilidades da classe positiva.
    Returns:
        dict: Dicionário com metricas (auc, report).
    """
    report = classification_report(y_test, y_pred, output_dict=True)
    auc = roc_auc_score(y_test, y_prob)
    
    print("\n--- Model Evaluation ---")
    print(f"ROC AUC: {auc:.4f}")
    if '1' in report:
        print(f"Precision (Risk): {report['1']['precision']:.4f}")
        print(f"Recall (Risk): {report['1']['recall']:.4f}")
    
    return {'auc': auc, 'report': report}

def print_reliability_report(metrics):
    """
    Imprime um relatório justificado de confiabilidade do modelo.
    """
    auc = metrics['auc']
    precision_risk = metrics['report']['1']['precision'] if '1' in metrics['report'] else 0.0
    
    print("\n[Relatório de Confiabilidade]")
    print(f"Métrica Principal (ROC AUC): {auc:.4f} (Aceitável > 0.70)")
    print(f"Justificativa: O modelo apresenta uma Precision de {precision_risk:.2f} na classe de Risco.")
    print(f"Isso significa que, de cada 100 alunos alertados, aprox. {int(precision_risk*100)} realmente têm risco de queda.")
    print("Essa confiabilidade permite intervenções focadas sem desperdiçar excessivamente recursos pedagógicos.")
