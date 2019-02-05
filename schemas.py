import models
from main import ma


class PollSchema(ma.ModelSchema):
    class Meta:
        model = models.Poll
        strict = True

class VoteSchema(ma.ModelSchema):
    class Meta:
        model = models.Vote
        strict = True

class ChoiceSchema(ma.ModelSchema):
    class Meta:
        model = models.Choice
        strict = True