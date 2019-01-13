import datetime
import os

from peewee import *

DATABASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'db'))
DATABASE = os.path.abspath(os.path.join(DATABASE_PATH, 'malware_domains.db'))

db = SqliteDatabase(DATABASE)


class MalwareDomains(Model):
    domain = TextField(primary_key=True)
    type = TextField()
    reference = TextField()
    created = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db  # This model uses the "people.db" database


class Log(Model):
    hash = TextField(primary_key=True)
    path = TextField()
    created = DateTimeField(default=datetime.datetime.now())

    class Meta:
        database = db


def init_database():

    if not os.path.exists(DATABASE_PATH):
        os.mkdir(DATABASE_PATH)

    try:
        db.create_tables([MalwareDomains, Log])
    except Exception as e:
        raise e
