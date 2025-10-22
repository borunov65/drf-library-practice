FROM python:3.12.6-slim
LABEL maintainer="borunov65@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN adduser \
    --disabled-password \
    --no-create-home \
    my_user

USER my_user
