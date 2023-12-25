FROM python:3.11.4

RUN wget https://dl.min.io/server/minio/release/linux-amd64/minio && \
    chmod +x minio && \
    mv minio /usr/local/bin/ && \
    wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    chmod +x mc && \
    mv mc /usr/local/bin/
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
COPY init.sh .
COPY api.py .
CMD ["sh", "init.sh"] && python flaskapi.py
