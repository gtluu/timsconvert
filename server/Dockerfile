FROM continuumio/miniconda3:4.11.0
MAINTAINER Mingxun Wang "mwang87@gmail.com"

RUN apt-get update && apt-get install -y build-essential

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/gtluu/pyimzML

COPY . /app
WORKDIR /app