FROM python:3.8-slim-buster

WORKDIR /app

ARG ensemble_container="antidote_ensemble_test"
ENV ensemble_container=$ensemble_container

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT [ "python3", "simulator_griefing.py"] 

#ZEND
