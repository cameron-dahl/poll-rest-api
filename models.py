from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeclarativeMeta
import json
from main import ma


db = SQLAlchemy()


# thanks to stackoverflow for this :)


class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())

choices = db.Table('choices',
    db.Column('choice_id', db.Integer, db.ForeignKey('choice.id'), primary_key=True),
    db.Column('poll_id', db.Integer, db.ForeignKey('poll.id'), primary_key=True)
)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(80))
    choices = db.relationship('Choice', secondary=choices, lazy='subquery', backref=db.backref('choices', lazy=True))

class PollSchema(ma.ModelSchema):
    class Meta:
        model = Poll

class ChoiceSchema(ma.ModelSchema):
    class Meta:
        model = Choice
