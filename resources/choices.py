from flask import Blueprint, request
from schemas import ChoiceSchema
from models import Choice
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