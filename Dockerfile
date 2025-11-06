FROM python:3.11-slim

ARG MLFLOW_VERSION

WORKDIR /app

RUN pip install --no-cache-dir mlflow==${MLFLOW_VERSION}

# Container internal port (mapped to host port via MLFLOW_PORT in mlflow.env)
EXPOSE 5000

CMD mlflow server \
    --backend-store-uri ${MLFLOW_BACKEND_STORE_URI} \
    --default-artifact-root ${MLFLOW_DEFAULT_ARTIFACT_ROOT} \
    --host 0.0.0.0

