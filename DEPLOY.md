# Guia de Deploy

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

7. **Atualizações Automáticas (CD)**:
   - Por padrão, o Render monitora a branch `main`.
   - **Sim**, qualquer `git push` para a `main` disparará automaticamente um novo build e deploy da sua aplicação.
   - Você pode desativar isso nas configurações do serviço ("Auto Deploy: No") se preferir controle manual.

---

## Estrutura de Arquivos Relevante para Deploy
- `Dockerfile`: Receita para criar a imagem do container.
- `docker-compose.yml`: Orquestração para ambiente local.
- `requirements.txt`: Lista de dependências Python.
- `app/`: Código fonte da API.
- `src/`: Código fonte do pipeline de ML.
