# -*- coding: utf-8 -*-
import datetime
import mongoengine as db
from mongoengine import connect


connect('partiayedy')


class User(db.Document):
    user_id = db.IntField(unique=True)
    name = db.StringField()
    phone = db.StringField(unique=True)
    email = db.EmailField()
    city = db.StringField()
    address = db.StringField()
    created = db.DateTimeField()


class Order(db.Document):
    user_id = db.IntField(required=True)
    status = db.IntField()
    persons_count = db.IntField(choices=[2, 4])
    dinners_count = db.IntField(choices=[5, 3])
    cuisine = db.StringField()
    comment = db.StringField()
    date = db.DateTimeField()
    created = db.DateTimeField(default=datetime.datetime.now)
