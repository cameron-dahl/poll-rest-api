from flask import Flask, request, jsonify, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import sys, json, time
from flask_cors import CORS
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://cameron:dbpassword@localhost/pollapp"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)
db = SQLAlchemy()
from flask_marshmallow import Marshmallow
ma = Marshmallow(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

def get_or_create(session, model, **kwargs):
    instance = db.session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance
# models
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
    choices = db.relationship('Choice', secondary=choices, lazy='subquery', backref=db.backref('poll', lazy=True))

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
        Poll_t = Poll(question=data['question'], choices=choices)
        db.session.add(Poll_t)
        db.session.commit()
        poll_schema = PollSchema()
        output = poll_schema.dump(Poll_t).data
        time.sleep(2)
        return {'poll': output}

class PollAPI(Resource):
    def get(self, id):
        data = request.json
        poll_t = Poll.query.filter_by(id=id).first()
        poll_schema = PollSchema()
        output = poll_schema.dump(poll_t).data
        return {'poll': output}
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
            return {'error': 'No poll matching with the ID of ' + str(id)}, 400
        db.session.commit()
        return '', 200

class ChoiceAPI(Resource):
    def delete(self, id):
        new_choice = Choice.query.get(id)
        if new_choice:
            db.session.delete(new_choice)
        else:
            return {'error': 'No choice matching with the ID of ' + str(id)}, 400
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
api.add_resource(PollAPI, '/api/polls/<int:id>/')
db.init_app(app)
db.create_all(app=app)

if __name__ == "__main__":
    app.run(debug=True)