FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências do Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Garante que o script de entrypoint tem permissão de execução (caso o chmod local falhe no contexto do docker)
RUN chmod +x docker-entrypoint.sh

# Expõe a porta do Streamlit
EXPOSE 8501

# Usa o script de entrypoint para rodar migrações e a aplicação
ENTRYPOINT ["./docker-entrypoint.sh"]
