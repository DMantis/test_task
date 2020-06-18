FROM python:3.8

COPY ./Pipfile ./Pipfile.lock ./
RUN pip install pipenv==2018.11.26 && pipenv install --clear --system --deploy

COPY ./src /src

ENV LOG_LEVEL info
ENV HTTP_SERVER_HOST 0.0.0.0
ENV HTTP_SERVER_PORT 8080

ENTRYPOINT python -m uvicorn src.app.main:app --host $HTTP_SERVER_HOST --port $HTTP_SERVER_PORT --log-level $LOG_LEVEL
