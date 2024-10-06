FROM python:3.11
WORKDIR /app
COPY . /app

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "/app/TIMSCONVERT_CMD.py"]