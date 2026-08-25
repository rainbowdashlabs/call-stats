FROM python:3.14-slim

WORKDIR /root

RUN pip install --no-cache-dir pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv sync

EXPOSE 8000
