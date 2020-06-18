FROM python:3.8

RUN apt-get update && \
    apt-get install -y libsecp256k1-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./Pipfile ./Pipfile.lock ./
RUN pip install pipenv==2018.11.26 && pipenv install --clear --system --deploy

COPY ./src /src

ENV LOG_LEVEL info
ENV HTTP_SERVER_PORT 8080

ENTRYPOINT python -m uvicorn src.app.main:app --host 127.0.0.1 --port $HTTP_SERVER_PORT --log-level $LOG_LEVEL
