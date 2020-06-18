# About 

Test interviews task.

It's a simple money transferring API service with possibilities of:  
* client creation with USD wallet;  
* money transfers between clients;  
* wallets topup from "external callback" emulation method.  

The app is made with FastAPI, so API docs might be accessed either through /docs
 or /redoc endpoints. OpenAPI specs are exportable via /openapi.json.
 
I decided to handle balances in client's table due to 'scalability' task 
requirement. It avoids clients balance recalculation on every request. 

# Notes

The transfers are made with usernames addressing to mitigate clients 
enumeration from 3rd parties.

## Known limitations
Due to time limit and the fact that task is not production one, several known 
limitations were allowed:

* For convenience of review process I committed some secrets to git: db dsn, 
jwt secret, etc. For sure, such things MUST NOT be committed in real production 
development. 
* No tests.
* Controller is not a singleton and may create several connections pools to 
database from base and auth routers - could be fixed with implementation of 
controller with singleton pattern.
* Inconsistent error messages format (fastapi's default 'detail' vs 'error 
message/code') - might be fixed by redefining fastapi exception handlers. More 
about time and attention task than actual work. 
* No verification on passwords safety.

# Configuration

Configuration is made through environment variables:

| Variable         | Definition                | Default                        |
|------------------|---------------------------|--------------------------------|
| HTTP_SERVER_PORT | http server port          | 8080                           | 
| LOG_LEVEL        | Python root logging level | info                           | 
| DB_DSN           | Postgres DSN              | postgresql://task:task@db/task |
| JWT_SECRET       | Secret for jwt auth       |                                |  

# Deployment

## Migrations

Migrations are distributed as raw sql versioned files in /sql directory. They 
could be applied with either flyway or yoyo-migrations. 

In case of docker-compose deployment (default one) flyway container is provided 
under 'migrations' one-shot service definition. 

## Docker + docker-compose

For the sake of simplicity the test task assumed docker-compose deployment. 

### Apply migrations

```bash
docker-compose up -d db
docker-compose up migrations
docker-compose up -d app
```

After that three steps services must be available on port 8080 (or user-defined 
HTTP_SERVER_PORT) on localhost. 