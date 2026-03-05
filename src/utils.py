from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

def get_model_instance(model_type, hyperparams):
    """
    Função para criar uma instância de modelo baseada na configuração.
    
    Args:
        model_type (str): Tipo do modelo ('random_forest', 'logistic_regression', 'gradient_boosting').
        hyperparams (dict): Dicionário de hiperparâmetros.
        
    Returns:
        model: Objeto do modelo instanciado.
        
    Raises:
        ValueError: Se model_type for desconhecido ou dependência estiver faltando.
    """
    if model_type == 'random_forest':
        return RandomForestClassifier(**hyperparams)
    
    elif model_type == 'logistic_regression':
        return LogisticRegression(**hyperparams)
    
    elif model_type == 'gradient_boosting':
        return HistGradientBoostingClassifier(**hyperparams)
    
    else:
        raise ValueError(f"Tipo de modelo desconhecido: {model_type}")
