FROM python:3.11-slim-buster

WORKDIR /app

#RUN apt-get update && apt-get install -y git
#
#RUN git clone https://github.com/GATO-Framework/shappie.git .

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

COPY src /app

CMD python run_bot.py
