from flask import render_template
from app import app, db
from app.forms import LoginForm
from app.models import Player


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form, title='login')


@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/leaderboard')
def leaderboard():
    players = Player.query.all()
    list_size = 0
    top_correct_guesses = []
    while list_size < 10:
        top_player = Player.query.filter_by(id=1).first()
        for player in players:
            if player.totalCorrectGuesses > top_player and player not in top_correct_guesses:
                top_player = player
        top_correct_guesses.append(top_player)
        list_size += 1
    return render_template('leaderboard.html', top_correct_guesses=top_correct_guesses, title='Home')
