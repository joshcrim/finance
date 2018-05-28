FROM ubuntu:16.04

MAINTAINER Joshua Crim "josh@jshcrm.com"

RUN apt-get update && apt-get install -y python3-pip python3.5-dev git

RUN git clone https://github.com/joshcrim/finance.git

WORKDIR /finance

RUN pip3 install -r requirements.txt

EXPOSE 5000

ENV FLASK_APP app.py

ENTRYPOINT [ "gunicorn", "--bind", "0.0.0.0:5000", "app:app"  ]
