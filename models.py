from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

'''
@login.user_loader
def load_player(id):
    return Player.query.get(int(id))
'''


class Player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered = db.column(db.Boolean)
    totalSongsPlayed = db.column(db.Integer)
    totalCorrectGuesses = db.column(db.Integer)
    monthlySongsPlayed = db.column(db.Integer)
    monthlyCorrectGuesses = db.column(db.Integer)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class GameRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hostID = db.Column(db.Integer)
    playerCount = db.Column(db.Integer)
    category = db.Column(db.String(64))
    isActive = registered = db.column(db.Boolean)
    private = registered = db.column(db.Boolean)
    code = db.Column(db.String(4))
    created = db.column(db.DateTime)
    updated = db.column(db.DateTime)

    def __repr__(self):
        return '<Room: {}>'.format(self.code)


class PlayerToGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.column(db.Integer)
    gameRoomID = db.column(db.Integer)
    points = db.column(db.Integer)

    def __repr__(self):
        return '<PlayerToGame: {}>'.format(self.points)


class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    playerID = db.column(db.Integer)
    gameRoomID = db.column(db.Integer)
    message = db.Column(db.String(64))
    created = db.column(db.DateTime)
    correctAnswer = db.column(db.Boolean)

    def __repr__(self):
        return '<' \
               'Message: {}>'.format(self.message)


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trackID = db.column(db.Integer)

    def __repr__(self):
        return '<' \
               'SongID: {}>'.format(self.trackID)


class SongToGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gameID = db.Column(db.Integer)
    songID = db.column(db.Integer)
    position = db.column(db.Integer)

    def __repr__(self):
        return '<' \
               'SongToGame: {}>'.format(self.position)
