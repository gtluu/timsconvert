FROM python:3.7
WORKDIR /app
COPY requirements_server.txt /app

RUN pip3 install -r requirements.txt
RUN pip3 install git+https://github.com/gtluu/pyimzML

COPY . /app

ENTRYPOINT ["python3", "/app/bin/run_server.py"]