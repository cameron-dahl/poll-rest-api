from flask import Flask, request, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
import sys, json, uuid, os
from flask_cors import CORS
from sqlalchemy_utils import IPAddressType
app = Flask(__name__)
POLL_DB_URI = os.environ['POLL_DB_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = POLL_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy()
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# models
class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    votes = db.relationship('Vote', backref='choice', lazy=True)


choices = db.Table('choices',
    db.Column('choice_id', db.Integer, db.ForeignKey('choice.id'), primary_key=True),
    db.Column('poll_id', db.Integer, db.ForeignKey('poll.id'), primary_key=True)
)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(80))
    choices = db.relationship('Choice', secondary=choices, lazy='subquery', backref=db.backref('poll', lazy=True, cascade="all"))
    edit_key = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    ip_vote_verification = db.Column(db.Boolean, default=True)


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(IPAddressType)
    choice_id = db.Column(db.String(), db.ForeignKey('choice.id'), nullable=False)

   

class PollSchema(ma.ModelSchema):
    class Meta:
        model = Poll
        strict = True

class ChoiceSchema(ma.ModelSchema):
    class Meta:
        model = Choice
        strict = True

class PollListAPI(Resource):
    def get(self):
        polls = Poll.query.all()
        for poll in polls:
            print(poll.question, file=sys.stdout)
        polls_schema = PollSchema(many=True)
        output = polls_schema.dump(polls).data
        return {'polls': output}
    def put(self):
        data = request.json
        print(data['choices'], file=sys.stdout)
        choices = []
        for choice in data['choices']:
            created_choice = Choice(text=choice)
            db.session.add(created_choice)
            db.session.commit()
            choices.append(created_choice)
        print(choices, file=sys.stdout)
        Poll_t = Poll(question=data['question'], choices=choices, edit_key=uuid.uuid4())
        db.session.add(Poll_t)
        db.session.commit()
        poll_schema = PollSchema()
        output = poll_schema.dump(Poll_t).data
        return {'poll': output}

class PollAPI(Resource):
    def get(self, id):
        data = request.json
        poll_t = Poll.query.filter_by(id=id).first()
        poll_schema = PollSchema()
        output = poll_schema.dump(poll_t).data
        return {'poll': output}
    def delete(self, id):
        poll_t = Poll.query.get(id)
        try:
            db.session.delete(poll_t)
        except:
            return {'error': 'That poll does not exist'}, 400
        db.session.commit()
        return '', 200
    def patch(self, id):
        poll_t = Poll.query.filter_by(edit_key=id).first()
        if not poll_t:
            return {'error': 'That poll does not exist'}, 400
        poll_schema = PollSchema()
        output = poll_schema.dump(poll_t).data
        return {'poll': output}

class ChoiceAPI(Resource):
    def delete(self, id):
        new_choice = Choice.query.get(id)
        if new_choice:
            db.session.delete(new_choice)
        else:
            return {'error': 'That choice does not exist'}, 400
        db.session.commit()
        return '', 200
class ChoiceListAPI(Resource):
    def get(self):
        choices = Choice.query.all()
        choice_schema = ChoiceSchema(many=True)
        output = choice_schema.dump(choices).data
        return {'choices': output}

api.add_resource(PollListAPI, '/api/polls/')
api.add_resource(ChoiceListAPI, '/api/choices/')
api.add_resource(ChoiceAPI, '/api/choices/<id>/')
api.add_resource(PollAPI, '/api/polls/<id>/')
db.init_app(app)
db.create_all(app=app)

if __name__ == "__main__":
    app.run(debug=True)
