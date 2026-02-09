# 🎓 Sistema de Alerta Preventivo (Modelo de Risco Acadêmico)

Este projeto implementa uma solução completa de Machine Learning para predição de risco de evasão escolar. A arquitetura é composta por um pipeline de treinamento robusto, uma API escalável e um dashboard interativo para consumo dos dados.

---

## 🚀 Funcionalidades

- **Pipeline de Treinamento Automatizado**:
  - Engenharia de features temporais.
  - Pré-processamento e limpeza de dados automatizados.
  - Treinamento com RandomForest e balanceamento de classes.
  - Serialização segura do modelo (`joblib`).

- **API RESTful (FastAPI)**:
  - Documentada via Swagger UI.
  - Autenticação JWT (Bearer Token).
  - Monitoramento de métricas via Prometheus.
  - Containerizada com Docker.

- **Dashboard Interativo (Streamlit)**:
  - Interface amigável para inputs de indicadores pedagógicos.
  - Login integrado e gestão de sessão.
  - Visualização clara do risco e probabilidade.

---

## 🛠️ Tech Stack

- **Linguagem**: Python 3.12
- **ML & Dados**: Scikit-Learn, Pandas, NumPy
- **API**: FastAPI, Uvicorn, Pydantic
- **Frontend**: Streamlit
- **Infraestrutura**: Docker, Docker Compose
- **Testes**: Pytest, Pytest-cov

---


Este documento descreve como realizar o deploy da API de Modelo de Risco tanto localmente quanto na nuvem (Render).

## 1. Deploy Local com Docker Compose

O `docker-compose.yml` incluído facilita a execução da aplicação localmente, garantindo que todas as configurações e dependências estejam isoladas.

### Pré-requisitos
- Docker instalado ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose (geralmente incluído no Docker Desktop)
- Arquivo `.env` na raiz do projeto (copie de `.env.example` se existir, e preencha com as credenciais).

### Passos
1. **Construir e Iniciar o Container**:
   No terminal, na raiz do projeto, execute:
   ```bash
   docker-compose up --build
   ```
   Isso irá construir a imagem Docker baseada no `Dockerfile` e iniciar o serviço na porta 8000.

2. **Acessar a API**:
   - Documentação Interativa (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)
   - Verificar Status: [http://localhost:8000/](http://localhost:8000/)

3. **Parar a Aplicação**:
   Pressione `Ctrl+C` no terminal ou execute:
   ```bash
   docker-compose down
   ```

---

## 2. Deploy na Nuvem (Render)

O [Render](https://render.com) é uma plataforma de nuvem que suporta deploy nativo de aplicações Dockerizadas.

### Passos
1. **Prepare o Repositório**:
   Certifique-se de que seu código (incluindo o `Dockerfile`) está enviado para o GitHub.

2. **Crie um Serviço no Render**:
   - Crie uma conta no [Render.com](https://render.com).
   - Clique em **"New +"** e selecione **"Web Service"**.
   - Conecte sua conta do GitHub e selecione o repositório `prj-datathon`.

3. **Configuração**:
   - **Runtime**: Selecione **Docker** (O Render detectará o `Dockerfile` automaticamente).
   - **Name**: Dê um nome para seu serviço (ex: `risk-model-api`).
   - **Region**: Escolha a mais próxima (ex: Ohio ou Frankfurt).
   - **Branch**: `main`.
   - **Instance Type**: `Free` (para testes/hobby) ou superior.

4. **Variáveis de Ambiente (Importante)**:
   - Como o arquivo `.env` não é enviado para o GitHub por segurança, você deve configurar as variáveis manualmente no Render.
   - Vá na aba **Environment** do seu serviço.
   - Adicione as chaves e valores que estão no seu `.env` local (ex: `SECRET_KEY`, `APP_USER`, `APP_PASS`).

5. **Deploy**:
   - Clique em **"Create Web Service"**.
   - O Render irá clonar o repo, construir a imagem Docker e iniciar o serviço.
   - Acompanhe os logs na dashboard. Quando aparecer "Build successful" e "Service live", sua API estará online.

6. **Acesso**:
   O Render fornecerá uma URL pública (ex: `https://risk-model-api.onrender.com`).
   - Acesse a documentação em: `https://<SEU-APP>.onrender.com/docs`

7. **Controle de Deploy (Build Filters)**:
   - Para evitar deploys desnecessários (ex: ao alterar apenas documentação), configure **Build Filters** no Render.
   - Vá em **Settings > Build & Deploy > Build Filter**.
   - Adicione caminhos que devem disparar o build, por exemplo:
     - `src/**`
     - `app/**`
     - `Dockerfile`
     - `requirements.txt`
   - Assim, commits que alteram apenas `README.md` ou `notebooks/` **não** dispararão um novo deploy.

---

## 3. Deploy do Dashboard (Streamlit Cloud)

O Dashboard `dashboard/app.py` pode ser hospedado gratuitamente no [Streamlit Community Cloud](https://streamlit.io/cloud).

### Passos
1. **Login**: Acesse com sua conta GitHub.
2. **Novo App**: Clique em "New app".
3. **Repositório**: Selecione este repositório (`prj-datathon`).
4. **Configurações**:
   - **Branch**: `main`
   - **Main file path**: `dashboard/app.py`
5. **Secrets (Variáveis de Ambiente)**:
   - Vá em "Advanced Settings" > "Secrets".
   - Adicione a URL da sua API hospedada no Render:
     ```toml
     API_URL = "https://risk-model-api.onrender.com"
     ```
   - O código do dashboard já está preparado para ler essa variável.
6. **Deploy**: Clique em "Deploy!".



---

## Estrutura de Arquivos Relevante para Deploy
- `Dockerfile`: Receita para criar a imagem do container.
- `docker-compose.yml`: Orquestração para ambiente local.
- `requirements.txt`: Lista de dependências Python.
- `app/`: Código fonte da API.
- `src/`: Código fonte do pipeline de ML.
