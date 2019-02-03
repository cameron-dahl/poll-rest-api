from flask import Blueprint, request
from models import *
from schemas import *
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
    def post(self):
        poll_t = Poll.query.filter_by(id=request.json['poll_id']).first()
        poll_t.verify_vote(request.remote_addr)