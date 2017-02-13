# Shortie

Simple API written in Python with Tornado framework and MongoDB as a storage to shortify URLs.

## How to run it?

#### Requirements
* Python >= 3.6
* MongoDB >= 3.2

#### Using Docker and docker-compose
Install docker and docker-compose
* [Docker installation guide](https://docs.docker.com/engine/installation/linux/)
* [docker-compose installation guide](https://docs.docker.com/compose/install/)

To start **Shortie** just run in your terminal:

```sh
$ docker-compose build && docker-compose up -d
```

Because of use [jwilder/nginx-proxy](https://github.com/jwilder/nginx-proxy) and docker-compose it's easy to scale the application:

```sh
$ docker-compose scale app=5
```

It also has a little impact on requests, each request should have added header `Host: shortie.local`.

#### Standard way

> **Make sure you have installed proper version of Python and MongoDB!**

1. Create and activate virtualenv
    ```sh
    $ python3 -m venv /path/to/virtual/env
    $ source /path/to/virtual/env/bin/activate
    ```
2. Install required python libraries
    ```sh
    $ pip install -r requirements.txt
    ```
3. Generate secret:
    ```sh
    $ python generate_secret.py
    ```
4. Set proper MongoDB connection string in constant variable *MONGO_URL* in file `shortie/settings/production.py`
5. Start **Shortie** application
    ```sh
    $ SHORTIE_SETTINGS=.production python -m shortie.run --port=8000 --host=0.0.0.0
    ```

## API endpoints

### Register user

Creates new user in database and returns authorization token.

```
POST /api/register
```

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| email | string | User email address |
| password | string | User password |

```json
{
    "email": "user_email",
    "password": "user_password"
}
```

#### CURL Example
```sh
$ curl -X POST -H "Host: shortie.local" -d '{"email": "user_email", "password": "user_password"}' localhost/api/register
```

#### Response
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE0ODY5NzAxNzUsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSJ9.gk5Iktvj-YK1kUkAS-g7gqmJy-mtXED6SCSiIPvjXFo"
}
```

---

### Authorize

Search for user in database and returns authorization token.

```
POST /api/auth
```

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| email | string | User email address |
| password | string | User password |

```json
{
    "email": "user_email",
    "password": "user_password"
}
```

#### CURL Example
```sh
$ curl -X POST -H "Host: shortie.local" -d '{"email": "user_email", "password": "user_password"}' localhost/api/auth
```

#### Response
```json
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE0ODY5NzAxNzUsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSJ9.gk5Iktvj-YK1kUkAS-g7gqmJy-mtXED6SCSiIPvjXFo"
}
```

---

### Generate shortie

Generates short url.

```
POST /api/shortie
```

#### Parameters

| Name | Type | Description |
| --- | --- | --- |
| url | string | URL address to shortify |
| name | string | *Optional* Custom user name for created shortie |

```json
{
    "url": "http://example.com"
}
```

```json
{
    "url": "http://example.com",
    "name": "myName"
}
```

#### CURL Example
```sh
$ curl -X POST -H "Host: shortie.local" -d '{"url": "http://example.com"}' localhost/api/shortie
```

#### Response
```json
{
    "shortie": "http://localhost/api/shortie/lejRe"
}
```

#### CURL Example
```sh
$ curl -X POST -H "Host: shortie.local" -d '{"url": "http://example.com", "name": "myName"}' localhost/api/shortie
```

#### Response
```json
{
    "shortie": "http://localhost/api/shortie/myName"
}
```

> Adding `Authorization` header assigns created shortie to user.

#### CURL Example
```sh
$ curl -X POST -H "Host: shortie.local" -H "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE0ODY5NzAxNzUsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSJ9.gk5Iktvj-YK1kUkAS-g7gqmJy-mtXED6SCSiIPvjXFo" -d '{"url": "http://example.com"}' localhost/api/shortie
```

---

### Get full URL

Returns full URL.

```
GET /api/shortie/:shortie
```

#### CURL Example
```sh
$ curl -H "Host: shortie.local" localhost/api/shortie/lejRe
```

#### Response
```json
{
    "url": "http://example.com"
}
```

---

### Get shortie info

```
GET /api/info
```

Returns all informations about single shortie or returns all user shorties.

| Name | Type | Description |
| --- | --- | --- |
| shortie | string | Shortie name |
| email | string | User email |

#### CURL Example
```sh
$ curl -H "Host: shortie.local" localhost/api/info?shortie=lejRe
```

#### Response
```json
{
    "url": "http://example.com"
    "shortie": "lejRe",
    "clicks: [
        "2017-02-12 18:44:13.60100"
    ],
    "created_at" "2017-02-11 12:45:23.98700"
}
```

#### CURL Example
```sh
$ curl -H "Host: shortie.local" localhost/api/info?email=test@test.com
```

#### Response
```json
{
    "shorties": [
        {
            "url": "http://example.com"
            "shortie": "lejRe",
            "clicks: [
                "2017-02-12 18:44:13.60100"
            ],
            "created_at" "2017-02-11 12:45:23.98700"
        },
        {
            "url": "http://test.com"
            "shortie": "myName",
            "clicks: [
                "2017-02-12 10:55:33.60100"
            ],
            "created_at" "2017-02-10 08:05:23.12870"
        }
    ]
}
```

## Tests

Tests are prepared to run in docker to make the dev/production environment clear.

To run tests go to `./tests` directory and run:
```sh
$ ./test.sh
```


