FROM python:3.11

RUN pip install -U pip

COPY src/ /src
WORKDIR /src

RUN pip install -r requirements.txt 

ENV PORT 8080
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 app:app