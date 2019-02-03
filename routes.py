from flask import Blueprint, request
from schemas import *
from models import *
import uuid, json
# Choices
choices_api = Blueprint('choices_api', __name__)

@choices_api.route('/<id>/', methods=['GET'])
def get_choice(id):
    data = request.json
    TheChoice = Choice.query.filter_by(id=id).first()
    choice_schema = ChoiceSchema()
    output = choice_schema.dump(TheChoice).data
    return {'choice': output}
@choices_api.route('/', methods=['DELETE'])
def delete(id):
    new_choice = Choice.query.get(id)
    if new_choice:
        db.session.delete(new_choice)
    else:
        return {'error': 'That choice does not exist'}, 400
    db.session.commit()
    return '', 200

@choices_api.route('/', methods=['GET'])
def get_all_choices():
    choices = Choice.query.all()
    choice_schema = ChoiceSchema(many=True)
    output = choice_schema.dump(choices).data
    return {'choices': output}

# Polls
polls_api = Blueprint('polls_api', __name__)

@polls_api.route('/', methods=['GET'])
def get_polls():
    polls = Poll.query.all()
    polls_schema = PollSchema(many=True)
    output = polls_schema.dump(polls).data
    return {'polls': output}
@polls_api.route('/', methods=['PUT'])
def create_poll():
    data = request.json
    choices = []
    Poll_t = Poll(question=data['question'], choices=choices, edit_key=uuid.uuid4())
    for choice in data['choices']:
        Poll_t.choices.append(Choice=choice) 
    db.session.add(Poll_t)
    db.session.commit()
    poll_schema = PollSchema()
    output = poll_schema.dump(Poll_t).data
    return {'poll': output}
@polls_api.route('/<id>/', methods=['GET'])
def get_poll(id):
    data = request.json
    poll_t = Poll.query.filter_by(id=id).first()
    poll_schema = PollSchema()
    output = poll_schema.dump(poll_t).data
    return {'poll': output}
@polls_api.route('/', methods=['DELETE'])
def delete_poll(id):
    poll_t = Poll.query.get(id)
    try:
        db.session.delete(poll_t)
    except:
        return {'error': 'That poll does not exist'}, 400
    db.session.commit()
    return '', 200
    
def modify_poll(id):
    # not done yet
    poll_t = Poll.query.filter_by(edit_key=id).first()
    if not poll_t:
        return {'error': 'That poll does not exist'}, 400
    poll_schema = PollSchema()
    output = poll_schema.dump(poll_t).data
    return {'poll': output}


# Votes
votes_api = Blueprint('votes_api', __name__)
@votes_api.route('/', methods=['GET'])
def get_votes():
    votes = Vote.query.all()
    vote_schema = VoteSchema(many=True)
    output = vote_schema.dump(votes).data
    return {'votes': output}
@votes_api.route('/', methods=['PUT'])
def create_vote():
    data = request.json
    choice = Choice.query.get(data['choice_id'])
    NewVote = Vote(ip_address=request.remote_addr)
    choice.votes.append(NewVote)
    db.session.add(choice)
    db.session.commit()
    poll_schema = VoteSchema()
    output = poll_schema.dump(NewVote).data
    return {"vote": output}

@votes_api.route('/verify/', methods=['GET'])
def verify_vote():
    poll_t = Poll.query.filter_by(id=request.json['poll_id']).first()
    poll_t.verify_vote(request.remote_addr)

dummy_data = Blueprint('dummy_data', __name__)
@dummy_data.route('/', methods=['GET'])
def dummy_api():
    '''
    This is to generate dummy data for the database. WARNING: THIS WILL DELETE ALL ENTRIES IN THE DATABASE!
    '''
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