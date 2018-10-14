FROM python:3.7.0

WORKDIR /usr/src/db-stream

COPY app/ app/
COPY tests/ tests/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
