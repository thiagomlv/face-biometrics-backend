# Use uma imagem base do Python
FROM thiagomlv/faceid-backend-base-final:v1

WORKDIR /Backend/API

# Copy API project
COPY app/ ./app/
COPY .env.db .

# Entrypoint
ENTRYPOINT ["./venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
