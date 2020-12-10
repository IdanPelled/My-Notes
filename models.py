from datetime import datetime
from typing import Type, Union

import bcrypt
from flask_login import UserMixin
from peewee import (CharField, DateTimeField, DoesNotExist,
                    ForeignKeyField, IntegrityError, Model, TextField)

from .config import COLORS, db


class Base(UserMixin, Model):
    class Meta:
        database = db


class User(Base):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()


class Color(Base):
    name = CharField(unique=True)
    value = CharField(unique=True)


class Note(Base):
    user_id = ForeignKeyField(User, backref='notes')
    color_id = ForeignKeyField(Color)
    last_save = DateTimeField(default=datetime.now)
    title = CharField()
    content = TextField()


CLASS_TYPES = Type[Union[User, Note, Color]]


# general
def create_db():
    db.create_tables([Note, User, Color], safe=True)
    existing_colors = [color.name for color in Color.select()]
    for name, val in COLORS.items():
        if name not in existing_colors:
            add_color(name, val)


def hash_password(password: bytes):
    """Hashes the password"""
    salt = bcrypt.gensalt(prefix=b'2b', rounds=12)
    return bcrypt.hashpw(password, salt)


def does_user_exist(user_id):
    try:
        get_user_by_id(int(user_id))
    except DoesNotExist:
        return False
    else:
        return True


def authenticate(user, password: bytes) -> bool:
    """Return True if password is
    correct, False otherwise"""
    try:
        return bcrypt.checkpw(password, user.password.encode('utf-8'))
    except DoesNotExist:
        return False


def create_welcome_note(user):
    add_note(title=f'Welcome {user.username}',
             content=f'Hey {user.username}, Thanks for using My Notes!',
             user_id=user.id,
             color_id='1')


# select
def get_user_by_username(username):
    """Returns a user by username"""
    user = User.select().where(User.username == username)
    try:
        return user.get()
    except DoesNotExist:
        return


def get_user_by_id(user_id: int):
    """Returns a user by id"""
    try:
        user = User.get(User.id == user_id)
    except DoesNotExist:
        return None
    else:
        return user


def get_note_by_id(note_id):
    """Returns a note by id"""
    try:
        note = Note.get(Note.id == note_id)
    except DoesNotExist:
        return None
    else:
        return note


def get_color_by_id(color_id):
    """Returns a color by id"""
    try:
        color = Color.get(Color.id == color_id)
    except DoesNotExist:
        return None
    else:
        return color


def get_user_by_note_id(note_id):
    """Returns a user by a note_id"""
    note = get_note_by_id(note_id)
    return note.user


def get_all_user_notes(user_id):
    """Returns a user's notes"""
    if does_user_exist(user_id):
        return Note.select().where(Note.user_id == user_id).order_by(Note.last_save.desc())
    raise DoesNotExist('User does not exist.')


def get_color_by_name(color):
    return Color.get(Color.name == color)


def get_all_colors():
    return Color.select()


# CREATE
def add_user(username, password, email):
    """Creates a new user"""
    hashed_password = hash_password(password)
    try:
        return User.create(username=username, password=hashed_password, email=email)

    except IntegrityError:
        return None


def add_color(color, val):
    """Creates a new color"""
    return Color.create(name=color, value=val)


def add_note(user_id, title, color_id='1', content=""):
    """Creates a new note"""
    return Note.create(user_id=user_id, title=title,
                       color_id=color_id, content=content)


# DELETE
def remove_user(user_id):
    """Deletes a user"""
    user: User = get_user_by_id(user_id)
    return user.delete_instance(recursive=True)


def remove_note(note_id):
    """Deletes a note"""
    note = get_note_by_id(note_id)
    return note.delete_instance(recursive=True)


def remove_color(color_id):
    """Deletes a color"""
    # WARNING !!!
    # this function will delete all
    # notes with the given color.
    color = get_color_by_id(color_id)
    return color.delete_instance(recursive=True)


# UPDATE
def update_last_save(note_id):
    """Updates a note's last_save date"""
    q = (Note.update({Note.last_save: datetime.now()})
         .where(Note.id == note_id))
    q.execute()


def save_note(note_id, content):
    """Saves a note"""
    update_last_save(note_id)
    Note.update({Note.content: content}).where(Note.id == note_id).execute()
