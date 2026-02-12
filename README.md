# 🎓 Prevendo Risco de Defasagem com Machine Learning (Datathon 2025)

## 1. Visão Geral do Projeto 
**Objetivo:** Previsão de Risco com Machine Learning.
Quais padrões nos indicadores permitem identificar alunos em risco antes de queda no desempenho ou aumento da defasagem? 

Construímos um modelo preditivo que mostra uma **probabilidade do aluno ou aluna entrar em risco de defasagem**.

**Solução Proposta:** Uma pipeline completa de Machine Learning (MLOps) que vai desde a ingestão dos dados brutos até o deploy de uma API em produção e um Dashboard interativo.

### Stack Tecnológica
*   **Linguagem:** Python 3.12
*   **Machine Learning:** scikit-learn, pandas, numpy, scipy
*   **API:** FastAPI (com autenticação JWT)
*   **Dashboard:** Streamlit (com monitoramento de Data Drift)
*   **Serialização:** joblib
*   **Testes:** pytest (com cobertura de código)
*   **Empacotamento:** Docker & Docker Compose
*   **CI/CD:** GitHub Actions
*   **Deploy Cloud:** Render (API) + Streamlit Cloud (Dashboard)

---

## 2. Estrutura do Projeto

A organização do repositório segue as melhores práticas de Engenharia de ML:

```
prj-datathon/
├── .github/workflows/      # CI Pipeline (GitHub Actions)
├── app/                    # Código da API (FastAPI)
│   ├── auth.py             # Lógica de Autenticação JWT
│   ├── main.py             # Entrypoint da API
│   ├── models/             # Modelos Treinados (.joblib)
│   ├── router.py           # Endpoints (/predict, /token)
│   ├── schemas.py          # Modelos Pydantic (Validação)
│   └── state.py            # Gerenciamento de Estado (Lifespan)
├── dashboard/              # Código do Frontend (Streamlit)
│   └── app.py              # Aplicação Interativa
├── data/                   # Dados (GitIgnored, exceto reference_data.csv)
├── notebooks/              # Jupyter Notebooks (EDA e Testes)
├── scripts/                # Scripts Auxiliares (Extração de Dados)
├── src/                    # Core do ML (Pacote Python)
│   ├── config.py           # Configurações Globais (Caminhos, Variáveis)
│   ├── data_loader.py      # Carregamento e Limpeza
│   ├── evaluation.py       # Avaliação do Modelo (Métricas e Relatórios)
│   ├── feature_engineering.py # Criação de Features Temporais
│   ├── modeling.py         # Wrapper do Modelo (RandomForest)
│   ├── preprocessing.py    # Pipeline de Transformação
│   └── train_pipeline.py   # Script de Treinamento
├── tests/                  # Testes Unitários e de Integração
├── Dockerfile              # Receita da Imagem Docker
├── docker-compose.yml      # Orquestração Local
├── pyproject.toml          # Gerenciamento de Dependências
├── requirements.txt        # Lista de Libs (Pip)
└── README.md               # Documentação Oficial
```

---

## 3. Instruções de Deploy (Como subir o ambiente)

### Opção A: Rodando Localmente com Docker (Recomendado)
A maneira mais fácil de testar a API isoladamente com ambiente containerizado.

**Pré-requisitos:** Docker e Docker Compose instalados.

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/ManoelSa/prj-datathon.git
    cd prj-datathon
    ```
2.  **Configure as Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz:
    ```env
    APP_USER=admin
    APP_PASS=admin123
    SECRET_KEY=sua_chave_secreta_super_segura
    API_URL=http://api:8000 # Para o docker-compose se conversarinternamente
    ```
3.  **Suba os contêineres:**
    ```bash
    docker-compose up --build
    ```
    *   **API:** Disponível em `http://localhost:8000/docs`

### Opção B: Rodando Localmente com Python (Venv)

1.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows: venv\Scripts\activate
    # Linux/Mac: source venv/bin/activate
    ```
2.  **Instale as dependências:**
    ```bash
    pip install . # Instala o projeto via pyproject.toml
    ```
3.  **Treine o Modelo (Gerar o .joblib):**
    ```bash
    python -m src.train_pipeline
    ```
4.  **Rode a API:**
    ```bash
    uvicorn app.main:app --reload
    ```
5.  **Rode o Dashboard (em outro terminal):**
    ```bash
    streamlit run dashboard/app.py
    ```

---

## 4. Exemplos de Chamadas à API

A API é protegida por token JWT. O fluxo é: **Login -> Token -> Predição**.

### 1. Autenticação (Obter Token)
**POST** `/token`
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```
**Resposta:**
```json
{"access_token": "eyJhbGciOi...", "token_type": "bearer"}
```

### 2. Predição (Analisar Risco)
**POST** `/predict` (Use o token no Header)
```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
       "IAA": 5.5, "IEG": 6.2, "IPS": 7.0, "IDA": 8.0, 
       "IPP": 4.5, "IPV": 6.1, "IAN": 5.0, "INDE": 6.5, 
       "Defasagem": 0.0
     }'
```
**Resposta:**
```json
{
  "prediction": 0,
  "probability": 0.12,
  "status": "Baixo Risco"
}
```

---

## 5. Etapas do Pipeline de Machine Learning

O pipeline de dados (`src/`) foi desenhado para ser modular e reproduzível:

1.  **Ingestão e Limpeza (`data_loader.py`):**
    *   Carrega múltiplas abas do Excel (2022, 2023, 2024).
    *   Padroniza nomes de colunas e remove caracteres inválidos.
    *   Converte tipos numéricos e trata nulos.

2.  **Engenharia de Features (`feature_engineering.py`):**
    *   **Abordagem Temporal:** O modelo não olha apenas para um ano isolado.
    *   Criamos pares de **(Ano T -> Ano T+1)**.
    *   *Features (X):* Indicadores do Ano T (ex: IAA 2022).
    *   *Target (Y):* Risco de Defasagem no Ano T+1 (Defasagem < 0).

3.  **Pré-processamento (`preprocessing.py`):**
    *   Pipeline do Scikit-Learn.
    *   `SimpleImputer`: Preenche valores faltantes com a mediana.
    *   `StandardScaler`: Normaliza as escalas dos indicadores (0-10) para evitar viés.

4.  **Treinamento e Seleção de Modelo (`train_pipeline.py`):**
    *   **Algoritmo:** Random Forest Classifier (Robustez e explicabilidade).
    *   **Métrica de Avaliação:** ROC-AUC (Melhor para classes desbalanceadas).
    *   O modelo final é salvo em `models/risk_model.joblib`.

5.  **Monitoramento (`dashboard/app.py`):**
    *   Compara a distribuição dos dados de Treino (Referência) com os dados novos chegando na API (Produção).
    *   Usa Teste KS (Kolmogorov-Smirnov) para alertar sobre **Data Drift** (mudança de padrão no comportamento dos alunos).
