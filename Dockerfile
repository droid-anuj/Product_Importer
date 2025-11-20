FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create upload directory
RUN mkdir -p /tmp/uploads

# Run Celery + FastAPI in same container
CMD ["sh", "-c", "celery -A celery_app worker --loglevel=info & uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
