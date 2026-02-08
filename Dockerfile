# Imagem base Python compatível com o projeto
FROM python:3.12-slim

# Impede o Python de gravar arquivos pyc e bufferizar stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Define o diretório de trabalho
WORKDIR /app

# Copia requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte e configura o pacote
COPY src/ ./src/
COPY pyproject.toml .

# Instala o pacote 'src' no ambiente Python do container
RUN pip install .

# Copia o restante da aplicação (API)
COPY app/ ./app/

# Expõe a porta da API
EXPOSE 8000

# Comando para rodar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
