FROM python:3.11.4-slim-bullseye

WORKDIR /app

COPY app ./app
COPY requirements.txt .

RUN pip install -r requirements.txt
ENV PYTHONPATH=/app/app

CMD ["python", "app/main.py"]
