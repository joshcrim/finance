FROM ubuntu:18.04

MAINTAINER Joshua Crim "josh@jshcrm.com"

RUN apt update && apt upgrade -y && apt install -y python3-pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 80
EXPOSE 5000

ENV FLASK_APP app.py

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
