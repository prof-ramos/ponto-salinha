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

# Garantir que o diretório de dados exista e tenha permissões
RUN mkdir -p /app/data && chown -R botuser:botgroup /app/data
VOLUME ["/app/data"]

# Copiar apenas o necessário do estágio de build com permissões corretas
COPY --chown=botuser:botuser --from=builder /root/.local /home/botuser/.local
COPY --chown=botuser:botuser src/ ./src/

ENV PATH=/home/botuser/.local/bin:$PATH
ENV DATABASE_PATH=/app/data/ponto.db
ENV PYTHONUNBUFFERED=1

USER botuser

# Healthcheck process
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python src/healthcheck.py || exit 1

CMD ["python", "src/main.py"]
