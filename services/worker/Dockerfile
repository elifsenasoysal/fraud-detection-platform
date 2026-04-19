FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy shared package
COPY shared/ /app/shared/

COPY services/worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e /app/shared/

COPY services/worker/app/ /app/app/

CMD ["python", "-m", "app.main"]
