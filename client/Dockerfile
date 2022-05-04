FROM python:3.7
WORKDIR /app
COPY requirements.txt /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3", "/app/bin/client.py"]