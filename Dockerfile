# syntax=docker/dockerfile:1

FROM python:3.9.6-buster

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENV REDIS_HOST="http://10.0.0.37/"

ENV MOEX_HOST="http://10.0.0.38:5000/"

ENV DB_HOST="http://10.0.0.35/"

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "8"]
