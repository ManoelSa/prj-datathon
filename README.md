# 🎓 SAPE - Sistema de Alerta Preventivo Escolar

## 1) Visão Geral do Projeto 
**Objetivo:** Identificar precocemente alunos em risco de evasão escolar usando Inteligência Artificial.

**Solução Proposta:** Construção de uma pipeline completa de Machine Learning, desde a correção automática de dados e engenharia de features temporais até o deploy do modelo em produção via API (FastAPI) e monitoramento via Dashboard (Streamlit).

**Stack Tecnológica:**
*   **Linguagem:** Python 3.12
*   **Frameworks de ML:** scikit-learn, pandas, numpy
*   **API:** FastAPI (Assíncrona com JWT)
*   **Serialização:** joblib
*   **Testes:** pytest
*   **Empacotamento:** Docker & Docker Compose
*   **Deploy:** Local (Docker) / Cloud (Render + Streamlit Cloud)
*   **Monitoramento:** Logs de Produção (CSV) + Dashboard de Drift

---

## 2) Estrutura do Projeto (Diretórios e Arquivos)

A organização do repositório segue as melhores práticas de Engenharia de ML:

```
prj-datathon/
├── .github/workflows/      # Automação de Testes e Deploy
├── app/                    # Código da API (FastAPI)
│   ├── auth.py             # Segurança (OAuth2 + JWT)
│   ├── main.py             # Entrypoint & Lifespan
│   ├── models/             # Artefatos do Modelo (.joblib)
│   └── router.py           # Endpoints (/predict, /history)
├── dashboard/              # Frontend (Streamlit)
│   └── app.py              # Dashboard de Predição e Monitoramento
├── data/                   # Dados (GitIgnored)
├── notebooks/              # Laboratório de Dados
├── scripts/                # Scripts Auxiliares
├── src/                    # Motor de Machine Learning (Pacote Reutilizável)
│   ├── config.py           # Central de Configuração
│   ├── data_loader.py      # Ingestão Robusta de Dados
│   ├── evaluation.py       # Relatórios de Confiabilidade Educacional
│   ├── feature_engineering.py # Lógica de Negócio (ex: Correção de Defasagem)
│   ├── modeling.py         # Wrapper do Modelo (RiskModel)
│   ├── preprocessing.py    # Pipeline de Tratamento (Imputer, Scaler)
│   └── train_pipeline.py   # Orquestrador de Treinamento
├── tests/                  # Testes Automatizados
├── Dockerfile              # Containerização
├── docker-compose.yml      # Orquestração Local
├── pyproject.toml          # Dependências do Projeto
├── README.md               # Documentação Oficial
└── requirements.txt        # Dependências de Produção
```

---

## 3) Instruções de Deploy (como subir o ambiente)

### Pré-requisitos
*   **Docker** e **Docker Compose** instalados.
*   (Opcional) Python 3.12 para rodar localmente sem Docker.

### Instalação e Execução via Docker (Recomendado)
Suba toda a infraestrutura (API + Dashboard) com um único comando:

```bash
docker-compose up --build
```
*   **API:** `http://localhost:8000/docs`
*   **Dashboard:** `http://localhost:8501`

### Instalação e Execução via Python Local

1.  **Prepare o Ambiente (Virtualenv):**
    ```bash
    # Crie o ambiente virtual
    python -m venv venv

    # Ative o ambiente
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```

2.  **Variáveis de Ambiente (.env):**
    Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo (ajuste as credenciais conforme desejado):
    ```ini
    APP_USER=admin
    APP_PASS=admin
    SECRET_KEY=sua_chave_secreta_aqui
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    API_URL=http://localhost:8000
    ```
    *(Você pode copiar do arquivo `.env.example` incluído no repositório)*

3.  **Instalação de Dependências:**
    Para garantir que **tanto** a API/Dashboard quanto o pacote de ML (`src`) sejam instalados corretamente:
    ```bash
    pip install -r requirements.txt  # Instala bibliotecas externas (FastAPI, Streamlit, etc)
    pip install -e .                 # Instala o nosso pacote 'src' em modo editável
    ```

4.  **Treinar e Validar o Modelo:**
    ```bash
    python src/train_pipeline.py
    # Output: Modelo salvo em app/models/risk_model.joblib e Relatório de Confiabilidade gerado.
    ```

5.  **Rodar a API:**
    ```bash
    uvicorn app.main:app --reload
    ```
6.  **Rodar o Dashboard:**
    ```bash
    streamlit run dashboard/app.py
    ```

---

## 4) Exemplos de Chamadas à API

A API é protegida via Token JWT.

### A. Autenticação (Obter Token)
**Input:** Usuário e Senha.
**Output:** Token de Acesso.

```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin123"
```

### B. Predição (Analisar Risco)
**Input:** Indicadores Educacionais no corpo do JSON.
**Output:** Probabilidade de Risco e Status (Alto/Baixo Risco) considerando o threshold.

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Authorization: Bearer SEU_TOKEN_AQUI" \
     -H "Content-Type: application/json" \
     -d '{
       "IAA": 5.5, "IEG": 6.2, "IPS": 7.0, "IDA": 8.0, 
       "IPP": 4.5, "IPV": 6.1, "IAN": 5.0, "INDE": 6.5, 
       "Defasagem": 0.0,
       "threshold": 0.5
     }'
```

**Exemplo de Resposta (Output):**
```json
{
  "prediction": 0,
  "probability": 0.12,
  "status": "Baixo Risco"
}
```

---

## 5) Etapas do Pipeline de Machine Learning

O pipeline de dados (`src/`) segue uma arquitetura modularizada:

1.  **Ingestão e Limpeza (`data_loader.py`):** Carregamento de dados brutos (Excel), padronização de colunas e unificação de safras (2022-2024).
2.  **Engenharia de Features (`feature_engineering.py`):** 
    *   Criação de datasets temporais (Ano T -> Target T+1).
    *   **Correção de Defasagem:** Aplicação de regra de negócio (Idade vs Fase Ideal) para corrigir dados inconsistentes.
3.  **Pré-processamento (`preprocessing.py`):** Imputação de nulos (Mediana) e normalização de escalas (StandardScaler) usando Pipelines do Scikit-Learn.
4.  **Seleção e Treinamento de Modelo (`modeling.py`):** Treinamento de um **Random Forest Classifier**, escolhido pela robustez em dados tabulares e capacidade de lidar com relações não lineares.
5.  **Avaliação (`evaluation.py`):** Geração do **Relatório de Confiabilidade Educacional**.
    *   **Métrica Principal (Recall):** O modelo prioriza a **Sensibilidade (Recall)**. No contexto educacional, o custo de não identificar um aluno em risco (Falso Negativo) é muito maior do que alertar um aluno que não precisava (Falso Positivo). A meta é garantir que nenhum aluno vulnerável seja "deixado para trás".
    *   **Threshold Ajustável:** Por padrão, o modelo classifica como "Risco" qualquer probabilidade acima de **0.5 (50%)**. Este limiar é parametrizável na API, permitindo ajustar a sensibilidade da "Rede de Segurança" conforme a capacidade de atendimento da equipe pedagógica (ex: baixar para 0.4 para capturar mais casos, aceitando mais falsos positivos).

---

## 6) Monitoramento Avançado (Observabilidade)

Além do Dashboard interativo, o projeto já inclui uma stack de monitoramento (Prometheus + Grafana) configurada via Docker. 
**Nota:** Atualmente, estas ferramentas rodam apenas em ambiente local (Docker Compose), servindo como base para futura observabilidade em nuvem.

### A. Prometheus (Coleta de Métricas)
*   **URL:** `http://localhost:9090`
*   **Função:** Coleta métricas técnicas da API (latência, contagem de requests, uso de memória) em tempo real.

### B. Grafana (Visualização)
*   **URL:** `http://localhost:3000`
*   **Função:** Dashboards visuais para acompanhar a saúde do sistema.
*   **Acesso:** Usuário `admin` / Senha `admin` (padrão inicial).

---

## 7) CI/CD e Deploy Automático

O projeto utiliza práticas modernas de **DevOps** para garantir qualidade e entrega contínua:

### Integração Contínua (CI) - GitHub Actions
Arquivo: `.github/workflows/ci.yml`
*   **Gatilho:** Todo *Pull Request* para a branch `main`.
*   **Ações:**
    1.  Setup do ambiente Python.
    2.  Instalação de dependências.
    3.  Execução automática de testes unitários (`pytest`).
    4.  Verificação de cobertura de código.
*   **Objetivo:** Impedir que código quebrado ou sem testes chegue à produção (Quality Gate).

### Entrega Contínua (CD)
A branch `main` é a fonte da verdade para produção.
1.  **API (Render):** Conectado ao repositório GitHub. A cada merge na `main`, o Render detecta o novo commit, reconstrói o Docker Container da API e faz o deploy automaticamente.
2.  **Dashboard (Streamlit Cloud):** Também observa a `main`. Atualizações no código do dashboard são refletidas quase instantaneamente na aplicação online.

---

## 8) Melhorias Futuras (Roadmap)

Para evoluir este MVP para uma solução Enterprise escalável, sugerimos os seguintes pontos:

*   **Autenticação:** Migrar do atual sistema de usuário único (variáveis de ambiente) para uma gestão de usuários via **Banco de Dados** (PostgreSQL/MySQL), permitindo múltiplos perfis e controle de acesso granular.
*   **Persistência de Dados:** Substituir os arquivos CSV (logs e métricas) por um **Data Warehouse** ou Banco Relacional estruturado. Isso garantirá integridade, backup automático e performance para grandes volumes de dados históricos.
*   **Monitoramento em Nuvem:** Migrar o stack Prometheus/Grafana para instâncias gerenciadas na nuvem, permitindo alertas via Email/Slack em caso de falhas ou degradação do modelo.
*   **MLflow (Experiment Tracking):** Implementar um servidor MLflow para rastrear experimentos, versionar modelos e comparar métricas de diferentes rodadas de treinamento de forma centralizada.
