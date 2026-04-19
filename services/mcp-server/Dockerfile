FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY shared/ /app/shared/

COPY services/mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install -e /app/shared/

COPY services/mcp-server/app/ /app/app/

EXPOSE 8001

CMD ["python", "-m", "app.main"]
