#auth serve Docker file

FROM python:3.11
WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 50051 8002

CMD ["sh", "-c", "python auth_server.py & uvicorn main:app --host 0.0.0.0 --port 8002"]