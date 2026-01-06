# Estágio de Build
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Estágio Final
FROM python:3.11-slim

WORKDIR /app

# Criar usuário não-root para segurança
RUN groupadd -r botgroup && useradd -r -g botgroup botuser

# Copiar apenas o necessário do estágio de build
COPY --from=builder /root/.local /home/botuser/.local
COPY src/ ./src/

# Garantir que o diretório de dados exista e tenha permissões
RUN mkdir -p /app/data && chown -R botuser:botgroup /app/data

ENV PATH=/home/botuser/.local/bin:$PATH
ENV DATABASE_PATH=/app/data/ponto.db
ENV PYTHONUNBUFFERED=1

USER botuser

CMD ["python", "src/main.py"]
