# DRF Library Practice

Django REST API project for managing books, borrowings and users writen in DRF.

## Installing using GitHub

Install PostgreSQL and create a database.
You can clone the repository with a single command:

```shell
git clone https://github.com/borunov65/drf-library-practice.git
cd drf-library-practice
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Swagger API Documentation
Available at:

```shell
http://localhost:8000/api/doc/swagger/
```


## Redoc API Documentation
Available at:

```shell
http://localhost:8000/api/doc/redoc/
```

## Build and run with Docker

Docker should be installed.

```shell
docker compose build
docker compose up
```

You can also pull the prebuilt image from Docker Hub:

```shell
docker pull borunov65/library:latest
docker run -it -p 8000:8000 ^
  -e POSTGRES_DB=library ^
  -e POSTGRES_USER=library ^
  -e POSTGRES_PASSWORD=library ^
  -e POSTGRES_HOST=db ^
  -e POSTGRES_PORT=5432 ^
  borunov65/library ^
  python manage.py runserver 0.0.0.0:8000
```

## Getting access

* create user  http://localhost:8000/api/users/register/
* get user token  http://localhost:8000/api/users/token/


## Run tests

```shell
docker compose run --rm library python manage.py test
```

## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing books and borrowings
* Creates books with titles and athors
* Creates borrowing with borrow_date, expected_return_date and actual_return_date
* Filtering books and borrowings

## Author

Ihor Borunov
Email: borunov65@gmail.com
