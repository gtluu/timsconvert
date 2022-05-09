FROM python:3.7
WORKDIR /client
COPY requirements.txt /client

RUN pip3 install -r requirements.txt

COPY . /client

ENTRYPOINT ["python3", "/client/bin/client.py"]