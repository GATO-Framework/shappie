FROM python:3.11-slim-buster

WORKDIR /usr/app

RUN apt-get update && apt-get install -y git

RUN git clone https://github.com/GATO-Framework/shappie.git .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh", "-c", "git pull && python ./src/entrypoint.py"]
