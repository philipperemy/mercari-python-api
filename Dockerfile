FROM python:3.7-slim
MAINTAINER Philippe Remy <premy.enseirb@gmail.com>

# https://stackoverflow.com/questions/36710459/how-do-i-make-a-comment-in-a-dockerfile
ARG DEBIAN_FRONTEND=noninteractive

COPY . /app/

WORKDIR /app

RUN pip3 install --upgrade pip
RUN pip3 install -e .

WORKDIR /app/examples

ENTRYPOINT [ "python3", "monitor.py" ]
