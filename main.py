from flask import Flask, request, jsonify, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import sys, json, uuid, os
from sqlalchemy_utils import IPAddressType
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
# Initalize Flask, SQLAlchemy, Marshmallow, and CORS
app = Flask(__name__)
db = SQLAlchemy()
POLL_DB_URI = os.environ['POLL_DB_URI']
app.config['SQLALCHEMY_DATABASE_URI'] = POLL_DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
ma = Marshmallow(app)
cors = CORS(app, resources={r'/api/*': {'origins': '*'}})

class Choice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String())
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = db.relationship('Poll', back_populates='choices')
    votes = db.relationship('Vote', back_populates='choice')

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(IPAddressType)
    choice_id = db.Column(db.Integer, db.ForeignKey('choice.id'))
    choice = db.relationship('Choice', back_populates='votes')

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(80))
    edit_key = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    ip_vote_verification = db.Column(db.Boolean, default=True)
    google_recaptcha = db.Column(db.Boolean, default=True)
    choices = db.relationship('Choice', back_populates='poll')

    def verify_vote(self, ip_address):
        '''
        This is a method for the verification of votes if the poll has the verification enabled. 
        It takes an IP address argument (usually from the remote request) so that it can query the database and check if there's any matches. 
        '''
        if self.ip_vote_verification:
           personHasVoted = db.session.query(Vote, Choice, Poll).filter(Poll.id==self.id).filter(Vote.ip_address==ip_address).first() is not None
           if personHasVoted:
               return True
           else:
               return False 
        return False

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

@app.route('/api/choices/<id>/', methods=['GET', 'DELETE', 'OPTIONS'])
def choice(id):
    if request.method == "GET":
        data = request.json
        TheChoice = Choice.query.filter_by(id=id).first()
        choice_schema = ChoiceSchema()
        output = choice_schema.dump(TheChoice).data
        return {'choice': output}
    elif request.method == "DELETE":
        new_choice = Choice.query.get(id)
        if new_choice:
            db.session.delete(new_choice)
        else:
         return {'error': 'That choice does not exist'}, 400
        db.session.commit()
        return '', 200

@app.route('/api/choices/', methods=['GET'])
def get_all_choices():
    choices = Choice.query.all()
    choice_schema = ChoiceSchema(many=True)
    output = choice_schema.dump(choices).data
    return jsonify(choices=output)

@app.route('/api/polls/', methods=['PUT', 'OPTIONS', 'GET'])
def polls():
    if request.method == "PUT":
        data = request.json
        Poll_t = Poll(question=data['question'], edit_key=uuid.uuid4(), ip_vote_verification=data['ip_vote_verification'], google_recaptcha=data['google_recaptcha'])
        for choice in data['choices']:
            new_choice = Choice(text=choice)
            Poll_t.choices.append(new_choice) 
        db.session.add(Poll_t)
        db.session.commit()
        poll_schema = PollSchema()
        output = poll_schema.dump(Poll_t).data
        return jsonify(poll=output)
    elif request.method == "OPTIONS":
        return '', 200
    elif request.method == "GET":
        polls = Poll.query.all()
        polls_schema = PollSchema(many=True)
        output = polls_schema.dump(polls).data
        return jsonify(polls=output)

@app.route('/api/poll/<id>/', methods=['GET', 'DELETE', 'PATCH', 'OPTIONS'])
def poll(id):
    if request.method == "GET":
        data = request.json
        poll_t = Poll.query.filter_by(id=id).first()
        poll_schema = PollSchema()
        output = poll_schema.dump(poll_t).data
        return jsonify(poll=output)
    elif request.method == "DELETE":
        data = request.json
        poll_t = Poll.query.get(id)
        try:
            db.session.delete(poll_t)
        except:
            return {'error': 'That poll does not exist'}, 400
        db.session.commit()
        return '', 200
    elif request.method == "PATCH":
        data = request.json
        if request.is_json:
            poll = Poll.query.filter_by(edit_key=id).first()
            poll.ip_vote_verification = data['ip_vote_verification']
            poll.google_recaptcha = data['google_recaptcha']
            db.session.commit()
            return 'Hi', 200
        else:
            poll_t = Poll.query.filter_by(edit_key=id).first()
            if not poll_t:
                return {'error': 'That poll does not exist'}, 400
            poll_schema = PollSchema()
            output = poll_schema.dump(poll_t).data
            return jsonify(poll=output)
    elif request.method == "OPTIONS":
        return '', 200
    
# Votes
@app.route('/api/votes/', methods=['GET', 'PUT'])
def votes():
    if request.method == "GET":
        votes = Vote.query.all()
        vote_schema = VoteSchema(many=True)
        output = vote_schema.dump(votes).data
        return jsonify(votes=output)
    elif request.method == "PUT":
        data = request.json
        choice = Choice.query.get(data['choice_id'])
        poll = Poll.query.get(choice.poll_id)
        verification = poll.verify_vote(request.remote_addr)
        if verification:
            return jsonify(error="You have already voted!"), 403
        NewVote = Vote(ip_address=request.remote_addr)
        choice.votes.append(NewVote)
        db.session.add(choice)
        db.session.commit()
        poll_schema = VoteSchema()
        output = poll_schema.dump(NewVote).data
        return jsonify(vote=output)

@app.route('/api/poll/<id>/votes/', methods=['GET'])
def get_votes(id):
    if request.method == "GET":
        votes = Vote.query.filter(Choice.poll_id==id)
        vote_schema = VoteSchema(many=True)
        output = vote_schema.dump(votes).data
        return jsonify(votes=output)

@app.route('/api/poll/<id>/choices/', methods=['GET'])
def get_choices(id):
    if request.method == "GET":
        choices = Choice.query.filter(Choice.poll_id==id)
        choices_schema = ChoiceSchema(many=True)
        output = choices_schema.dump(choices).data
        return jsonify(choices=output)

@app.route('/api/votes/verify', methods=['GET'])
def verify_vote():
    poll_t = Poll.query.filter_by(id=request.json['poll_id']).first()
    poll_t.verify_vote(request.remote_addr)

db.init_app(app)
db.create_all(app=app)
if __name__ == '__main__':
    app.run(debug=True)
