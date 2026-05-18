FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY train_cnn.py .
COPY train_triage.py .
COPY model_contract.json .

CMD ["python", "train_cnn.py"]
