from app import db, login
from flask_login import UserMixin


@login.user_loader
def load_user(id):
    return Player.query.get(int(id))


class Player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16))
    email = db.Column(db.String(45))

    def __repr__(self):
        return '<Player {}>'.format(self.name)
