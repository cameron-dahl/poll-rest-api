from flask import Flask, request, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from flask_cors import CORS
from sqlalchemy_utils import IPAddressType
from flask_marshmallow import Marshmallow
import sys, json, uuid, os
app = Flask(__name__)
POLL_DB_URI = os.environ['POLL_DB_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = POLL_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy()
ma = Marshmallow(app)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = db.relationship('Poll', back_populates='choices')
    votes = db.relationship('Vote', back_populates='choice')

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(80))
    edit_key = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    ip_vote_verification = db.Column(db.Boolean, default=True)
    choices = db.relationship('Choice', back_populates='poll')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(IPAddressType)
    choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'))
    choice = db.relationship('Choice', back_populates='votes')

class PollSchema(ma.ModelSchema):
    class Meta:
        model = Poll
        strict = True

class VoteSchema(ma.ModelSchema):
    class Meta:
        model = Vote
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
        # TODO: Change this choices creation to be more model-based than SQL-y
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

class VoteListAPI(Resource):
    def get(self):
        votes = Vote.query.all()
        vote_schema = VoteSchema(many=True)
        output = vote_schema.dump(votes).data
        return {'votes': output}
    def put(self):
        data = request.json
        # TODO this should be changed to be an append on choice's model object instead of being a direct obj creation
        # TODO ip_address can't come from a POST param, otherwise it could be easily faked by a malicious user
        # need to pull the IP address from the request directly
        # ---> request.remote_addr should be the parameter we need here
        NewVote = Vote(ip_address=data['ip_address'], choice_id=data['choice_id'])
        db.session.add(NewVote)
        db.session.commit()
        poll_schema = VoteSchema()
        output = poll_schema.dump(NewVote).data
        return {'vote': output}

class VerifyVoteAPI(Resource):
    def post(self):
        poll = Poll.query.get(request.json['poll_id'])
        if not poll:
            return {'error': 'That poll does not exist'}, 404
        if poll.ip_vote_verification:
            personHasVoted = db.session.query(Vote, Choice, Poll).filter(Poll.id==poll.id).filter(Vote.ip_address==request.json['ip_address']).first() is not None
            if personHasVoted:
                return {'error': 'You have already voted on this poll.'}, 403
        return {'message': 'This is not done yet.'}
        

class ChoiceAPI(Resource):
    def get(self, id):
        data = request.json
        TheChoice = Choice.query.filter_by(id=id).first()
        choice_schema = ChoiceSchema()
        output = choice_schema.dump(TheChoice).data
        return {'choice': output}
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

class DummyDataAPI(Resource):
    def get(self):
        db.session.query(Vote).delete()
        db.session.query(Choice).delete()
        db.session.query(Poll).delete()

        poll = Poll(question='Cats or Dogs?', edit_key=uuid.uuid4(), ip_vote_verification=True)
        cats = Choice(text='Cats')
        dogs = Choice(text='Dogs')
        poll.choices.append(cats)
        poll.choices.append(dogs)
        cats.votes.append(Vote(ip_address='127.0.0.1'))
        cats.votes.append(Vote(ip_address='192.168.86.1'))
        dogs.votes.append(Vote(ip_address='127.0.0.1'))
        dogs.votes.append(Vote(ip_address='192.168.86.1'))
        db.session.add(poll)

        db.session.commit()

api.add_resource(PollListAPI, '/api/polls/')
api.add_resource(ChoiceListAPI, '/api/choices/')
api.add_resource(ChoiceAPI, '/api/choices/<id>/')
api.add_resource(PollAPI, '/api/polls/<id>/')
api.add_resource(VoteListAPI, '/api/votes/')
api.add_resource(VerifyVoteAPI, '/api/votes/verify/')
api.add_resource(DummyDataAPI, '/api/dummydata/')
db.init_app(app)
db.create_all(app=app)

if __name__ == '__main__':
    app.run(debug=True)
