FROM python:3.9.13-slim

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install --no-cache-dir 'mlflow'

CMD mlflow server \
    --backend-store-uri sqlite:////app/mlruns.db \
    --default-artifact-root s3://$MLFLOW_S3_BUCKET_NAME/artifacts \
    --host 0.0.0.0