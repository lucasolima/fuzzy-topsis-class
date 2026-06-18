#!/bin/bash
set -e

# Esperar o banco de dados ficar pronto
echo "Aguardando o banco de dados..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "Postgres está indisponível - aguardando..."
  sleep 2
done

echo "Executando migrações..."
alembic upgrade head

echo "Iniciando a aplicação..."
exec streamlit run main.py
