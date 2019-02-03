from main import db
from sqlalchemy_utils import IPAddressType
from sqlalchemy.dialects.postgresql import UUID
# this is a change

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
    choices = db.relationship('Choice', back_populates='poll')

    def verify_vote(self, ip_address):
        '''
        This is a method for the verification of votes if the inital poll has the verification enabled. It takes a poll ID argument and an IP address. 
        '''
        if not poll:
            return {'error': 'That poll does not exist'}, 404
        if poll.ip_vote_verification:
            personHasVoted = db.session.query(Vote, Choice, Poll).filter(Poll.id==self.id).filter(Vote.ip_address==ip_address).first() is not None
            if personHasVoted:
                return {'error': 'You have already voted on this poll.'}, 403
        return {'message': 'IP Vote verification is not enabled for this poll.'}