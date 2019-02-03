
class DummyDataAPI(Resource):
    '''
    This is to generate dummy data for the database. WARNING: THIS WILL DELETE ALL ENTRIES IN THE DATABASE!
    '''
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