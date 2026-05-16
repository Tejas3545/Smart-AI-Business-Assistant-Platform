FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-web.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app

EXPOSE 8000

# Use the PORT env var provided by Render, default to 8000 when not set.
# Use shell form so environment variable expansion works inside the container.
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
