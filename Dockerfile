FROM python:3.11.4-slim-bullseye

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app ./app
COPY requirements.txt .

RUN pip install -r requirements.txt
ENV PYTHONPATH=/app

CMD ["python", "app/main.py"]
