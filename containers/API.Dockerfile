FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
