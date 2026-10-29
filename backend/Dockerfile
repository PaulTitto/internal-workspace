# Multi-stage/Slim production Dockerfile for Backend Flask
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

WORKDIR /app

# Install system dependencies if required (e.g. curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

# Ensure instance directory exists for SQLite database volume mount
RUN mkdir -p /app/instance

EXPOSE 5001

# Run with Gunicorn WSGI production server
CMD ["gunicorn", "-b", "0.0.0.0:5001", "--workers", "2", "--threads", "4", "app:create_app()"]
