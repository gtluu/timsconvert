FROM ubuntu:18.04
FROM mono:latest


RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential

RUN pip3 install flask
RUN pip3 install gunicorn
RUN pip3 install requests

RUN apt-get install -y git

RUN apt-get install zip unzip

RUN pip3 install -r requirements.txt

COPY . /app
WORKDIR /app