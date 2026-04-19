FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package first (for caching)
COPY shared/ /app/shared/

# Copy requirements and install dependencies
COPY services/api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install shared package
RUN pip install -e /app/shared/

# Copy application code
COPY services/api-gateway/app/ /app/app/
COPY services/api-gateway/alembic.ini /app/alembic.ini
COPY services/api-gateway/alembic/ /app/alembic/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
