# MarketingAI Backend - imagem Docker
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/app/backend

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
COPY ia_pipeline/requirements.txt ./ia_pipeline/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt -r ia_pipeline/requirements.txt \
    && python -m playwright install --with-deps chromium

COPY backend ./backend
COPY ia_pipeline ./ia_pipeline

WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
