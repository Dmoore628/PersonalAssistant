# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install archi_core and runtime deps
COPY libs/archi_core /tmp/archi_core
RUN pip install --no-cache-dir /tmp/archi_core && rm -rf /tmp/archi_core
RUN pip install --no-cache-dir fastapi uvicorn[standard] neo4j pika

COPY services/memory_agent /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
