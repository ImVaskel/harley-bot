FROM python:3.9-slim-buster
LABEL maintainer="vaskel <contact@vaskel.xyz>"

RUN apt update \
    && apt-get install gcc git curl -y \
    && pip install --upgrade pip setuptools wheel poetry \
    && poetry config virtualenvs.create false

WORKDIR /app
COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-dev

COPY . .
CMD ["python", "main.py"]
