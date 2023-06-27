FROM python:3.11-slim-buster

WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

EXPOSE 8501

CMD streamlit run dashboard/dashboard.py
