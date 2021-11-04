FROM python:3.9.6

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend

COPY Pipfile /backend/
COPY Pipfile.lock /backend/
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile
COPY . /backend/
