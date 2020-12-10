import os
from urllib.parse import urlparse

from peewee import PostgresqlDatabase

url = urlparse(os.environ['DATABASE_URL'])
SECRET_KEY = os.environ['SECRET_KEY']

db = PostgresqlDatabase(
    url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)

COLORS = {
    'white': '#f2f2f2',
    'yellow': '#E9FF86',
    'blue': '#80FFD7',
    'orange': '#FFD986',
    'green': '#ACFF86',
    'purple': '#E085FF'
}
