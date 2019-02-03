from main import *
from flask import Blueprint
from flask_restful import Resource, Api
from models import *
polls_api = Blueprint('polls_api', __name__)

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
        choices = []
        Poll_t = Poll(question=data['question'], choices=choices, edit_key=uuid.uuid4())
        for choice in data['choices']:
            Poll_t.choices.append(Choice=choice) 
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




