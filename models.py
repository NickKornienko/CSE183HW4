"""
This file defines the database models
"""
import datetime
from email.policy import default

from . common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None


db.define_table(
    'address',
    Field('user_email', default=get_user_email),
    Field('first', requires=IS_NOT_EMPTY()),
    Field('last', requires=IS_NOT_EMPTY()),
    Field('phone', requires=IS_NOT_EMPTY()),
)

db.address.id.readable = db.address.id.writable = False
db.address.user_email.readable = db.address.user_email.writable = False
db.address.phone.readable = db.address.phone.writable = False

db.define_table(
    'phone',
    Field('user_email', default=get_user_email),
    Field('phone_number', requires=IS_NOT_EMPTY()),
    Field('kind', requires=IS_NOT_EMPTY()),
)

db.phone.id.readable = db.phone.id.writable = False
db.phone.user_email.readable = db.phone.user_email.writable = False


db.commit()
