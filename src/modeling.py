import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
from .config import RANDOM_STATE

class RiskModel:
    """
    Wrapper para o modelo de classificação de risco (Random Forest).
    
    Encapsula um RandomForestClassifier do scikit-learn com hiperparâmetros pré-definidos para
    lidar com desbalanceamento de classes. Foca estritamente em treino e predição.

    Attributes:
        model (RandomForestClassifier): O estimador subjacente.
        feature_cols (list): Lista de nomes das features utilizadas no treinamento.
    """
    def __init__(self, model=None, n_estimators=200, max_depth=5):
        if model:
            self.model = model
        else:
            self.model = RandomForestClassifier(
                n_estimators=n_estimators, 
                max_depth=max_depth, 
                class_weight='balanced', 
                random_state=RANDOM_STATE
            )
        self.feature_cols = None
        
    def train(self, X_train, y_train):
        """
        Treina o modelo com os dados fornecidos.

        Armazena internamente a lista de colunas (features) para garantir consistência na predição.

        Args:
            X_train (pd.DataFrame): Features de treinamento.
            y_train (pd.Series): Rótulos (targets) de treinamento.
        """
        self.feature_cols = X_train.columns.tolist()
        self.model.fit(X_train, y_train)
        
    def predict(self, X):
        """
        Realiza predições de classe (0 ou 1).

        Args:
            X (pd.DataFrame): Dados de entrada.

        Returns:
            np.ndarray: Array com as classes preditas.
        """
        return self.model.predict(X)
        
    def predict_proba(self, X):
        """
        Retorna a probabilidade da classe positiva (Risco).

        Args:
            X (pd.DataFrame): Dados de entrada.

        Returns:
            np.ndarray: Array com as probabilidades da classe 1.
        """
        return self.model.predict_proba(X)[:, 1]
    
    def save(self, filepath):
        """
        Serializa e salva o modelo treinado em disco.

        Args:
            filepath (str): Caminho de destino para o arquivo (.joblib).
        """
        joblib.dump(self.model, filepath)
        print(f"Modelo salvo em {filepath}")
        
    def load(self, filepath):
        """
        Carrega um modelo treinado do disco.

        Args:
            filepath (str): Caminho do arquivo de modelo salvo.
        """
        self.model = joblib.load(filepath)
        print(f"Modelo carregado de {filepath}")
