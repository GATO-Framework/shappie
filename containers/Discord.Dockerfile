FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app
COPY scripts/run_bot.py /app/entrypoint.py

CMD python entrypoint.py
