FROM python:3

WORKDIR /usr/src

COPY app/ app/
COPY tests/ tests/
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt
