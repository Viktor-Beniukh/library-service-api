# Library Service API

API service for library management with established procedure of borrowing 
and returning of books, as well as system of payment for loans written in DRF


### Installing using GitHub

Install PostgreSQL and create db

```shell
git clone https://github.com/Viktor-Beniukh/library-service-api.git
cd library-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver   
```
You need to create `.env` file and add there the variables with your according values:
- `POSTGRES_DB`: this is databases name;
- `POSTGRES_USER`: this is username for databases;
- `POSTGRES_PASSWORD`: this is username password for databases;
- `POSTGRES_HOST`: this is host name for databases;
- `POSTGRES_PORT`: this is port for databases;
- `SECRET_KEY`: this is Django Secret Key - by default is set automatically when you create a Django project.
                You can generate a new key, if you want, by following the link: `https://djecrety.ir`.
- `TELEGRAM_BOT_TOKEN`: your token received when creating the Telegram bot;
- `TELEGRAM_CHAT_ID`: chat_id received when creating the Telegram bot;
- `CELERY_BROKER_URL` & `CELERY_RESULT_BACKEND`: they're used to create periodic tasks. Have to install Celery & Redis;
- `STRIPE_PUBLIC_KEY` & `STRIPE_SECRET_KEY`: your keys received after registration on the Stripe website.


## Run with docker

Docker should be installed

- Create docker image: `docker-compose build`
- Run docker app: `docker-compose up`


## Getting access

- Create user via /api/user/register/
- Get access token via /api/user/token/


## Features

- JWT authentication;
- Admin panel /admin/;
- Documentation is located at /api/doc/swagger/;
- Managing books, borrowings and payments;
- Creating books;
- Creating borrowings and returning books;
- Creating borrowing payments;
- Filtering books, borrowings.

### How to create superuser
- Run `docker-compose up` command, and check with `docker ps`, that 2 services are up and running;
- Create new admin user. Enter container `docker exec -it <container_name> bash`, and create in from there;


### What do APIs do
- [GET] /api/library/books/ - obtains a list of books with the possibility of filtering by title;
- [GET] /api/library/books/<id>/ - obtains a detail of book;
- [POST] /api/library/books/ - creates a book;

- [GET] /borrowing/ - obtains a list of borrowings with the possibility of filtering by user_id&is_active;
- [GET] /borrowing/?user_id=...&is_active=.../ - get borrowings by user id and whether is borrowing still active;
- [GET] /borrowing/<id>/ - get specific borrowing;
- [POST] /borrowing/ - creates a borrowing of books;
- [POST] /borrowing/<id>/return/ - set actual return date of books;

- [GET] /payment/ - obtains a list of borrowing payments;
- [GET] /payment/<id>/ - obtains a detail of borrowing payment;
- [POST] /payment/ - creates a payment of books borrowing;
- [POST] /payment/<id>/create-session/ - redirects to payment page;

- [GET] /success/ - check successful stripe payment;
- [GET] /cancelled/ - return payment paused message;

- [POST] /api/user/register/ - creates new users;
- [POST] /api/user/token/ - creates token pair for user;
- [POST] /api/user/token/refresh/ - refresh JWT token;
- [GET]  /api/user/me/ - get my profile info;


### Checking the endpoints functionality
- You can see detailed APIs at swagger page: via /api/doc/swagger/


## Check project functionality

Superuser credentials for test the functionality of this project:
- email address: `migrated@admin.com`;
- password: `adminpassword`.


## Create token pair for user

Token page: via /api/user/token/

Enter:
- email address: `migrated@admin.com`;
- password: `adminpassword`.
