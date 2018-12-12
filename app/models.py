from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


@login.user_loader
def load_player(id):
    return player.query.get(int(id))


class player(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    registered = db.Column(db.Boolean)
    totalSongsPlayed = db.Column(db.Integer)
    totalCorrectGuesses = db.Column(db.Integer)
    monthlySongsPlayed = db.Column(db.Integer)
    monthlyCorrectGuesses = db.Column(db.Integer)

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class game_room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), index=True, unique=True)
    hostID = db.Column(db.Integer)
    playerCount = db.Column(db.Integer)
    category = db.Column(db.String(64))
    isActive = db.Column(db.Boolean)
    private = db.Column(db.Boolean)
    code = db.Column(db.String(4))
    timer = db.Column(db.Integer)
    current_song = db.Column(db.String(200))
    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)

    def __repr__(self):
        return '<Room: {}>'.format(self.code)


class player_to_game(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.Integer)
    gameRoomID = db.Column(db.Integer)
    points = db.Column(db.Integer)

    def __repr__(self):
        return '<PlayerToGame: {}>'.format(self.points)


class chat_message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    playerID = db.Column(db.Integer)
    gameRoomID = db.Column(db.Integer)
    message = db.Column(db.String(64))
    created = db.Column(db.DateTime)
    correctAnswer = db.Column(db.Boolean)

    def __repr__(self):
        return '<Message: {}>'.format(self.message)


class song(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist = db.Column(db.String(300))
    title = db.Column(db.String(300))
    link = db.Column(db.String(300))
    startTime = db.Column(db.Integer)

    def __repr__(self):
        return '<SongID: {}>'.format(self.trackID)


class song_to_game(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gameID = db.Column(db.Integer)
    songID = db.Column(db.Integer)
    position = db.Column(db.Integer)

    def __repr__(self):
        return '<SongToGame: {}>'.format(self.position)
