from dotenv import load_dotenv
from os import environ

load_dotenv()

SECRET_KEY = 'abcd'

if environ.get('DEV') == '1':
    DEV = True
else:
    DEV = False

TIME_LIMIT = 1000
MEMORY_LIMIT = 256*1024
LANGUAGE = 'PYTHON'

POSTGRES_USERNAME = environ.get('POSTGRES_USERNAME')
POSTGRES_PASSWORD = environ.get('POSTGRES_PASSWORD')
POSTGRES_HOST = environ.get('POSTGRES_HOST')
POSTGRES_PORT = environ.get('POSTGRES_PORT')
POSTGRES_DB = environ.get('POSTGRES_DB')

SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

GMAIL_EMAIL = environ.get('GMAIL_EMAIL')
GMAIL_APP_PASSWORD = environ.get('GMAIL_APP_PASSWORD')

INITIAL_ADMIN_EMAIL = environ.get('INITIAL_ADMIN_EMAIL')
