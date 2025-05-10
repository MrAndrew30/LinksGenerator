FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY setup.py .
COPY requirements.txt .
COPY links_generator/ ./links_generator/

RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install -r requirements.txt

CMD ["run-bot"]