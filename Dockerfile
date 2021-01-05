FROM python:3.8-slim

WORKDIR /app

RUN pip3 install pipenv

COPY . .

RUN pipenv install --dev

RUN pipenv run python3 model.py

EXPOSE 8069
ENTRYPOINT pipenv run python3 app.py