import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import SimpleImputer

class TemporalPreprocessor(BaseEstimator, TransformerMixin):
    """
    Transformador para pré-processamento de dados temporais, focado em imputação.

    Este transformador utiliza a estratégia de mediana para imputar valores faltantes (NaN)
    nas colunas especificadas. É compatível com o pipeline do Scikit-Learn.

    Attributes:
        feature_cols (list): Lista de nomes das colunas a serem processadas.
        imputer (SimpleImputer): Objeto imputer do sklearn configurado com estratégia 'median'.
    """
    def __init__(self, feature_cols=None):
        self.feature_cols = feature_cols
        self.imputer = SimpleImputer(strategy='median')
        
    def fit(self, X, y=None):
        """
        Ajusta o imputer aos dados de treino.

        Se feature_cols não for fornecido na inicialização, ele assume todas as colunas de X.

        Args:
            X (pd.DataFrame): Dados de treino.
            y (pd.Series, optional): Alvo (não utilizado, mantido para compatibilidade com sklearn).

        Returns:
            self: O próprio objeto ajustado.
        """
        if self.feature_cols is None:
            self.feature_cols = X.columns.tolist()
        self.imputer.fit(X[self.feature_cols])
        return self
    
    def transform(self, X):
        """
        Aplica a imputação aos dados.

        Args:
            X (pd.DataFrame): Dados para transformar.

        Returns:
            pd.DataFrame: Novo DataFrame com valores imputados e colunas/índices preservados.
        """
        X_copy = X.copy()
        X_imputed = self.imputer.transform(X_copy[self.feature_cols])
        return pd.DataFrame(X_imputed, columns=self.feature_cols, index=X.index)


