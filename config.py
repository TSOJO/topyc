from os import environ

if environ.get('DEV') == '1':
    DEV = True
else:
    DEV = False

TIME_LIMIT = 1000
MEMORY_LIMIT = 256*1024
LANGUAGE = 'PYTHON'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:root@localhost/topyc'