from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RoomForm, RegistrationForm
from app.models import player, player_to_game, game_room, song, song_to_game, chat_message
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', form=form, title='Register')


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form, title='login')


@app.route('/home')
def home():
    return render_template('home.html', title='Home')


@app.route('/leaderboard')
def leaderboard():
    players = player.query.all()
    list_size = 1
    top_correct_guesses = []
    while list_size <= 10:
        top_player = player.query.filter_by(id=1).first()
        for person in players:
            if player.totalCorrectGuesses > top_player and person not in top_correct_guesses:
                top_player = person
        player_to_add = str(list_size) + ". " + top_player.username
        top_correct_guesses.append(player_to_add)
        list_size += 1
    return render_template('leaderboard.html', top_correct_guesses=top_correct_guesses, title='Home')


@app.route('/create_room')
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        cr = game_room(name=form.name.data, category=form.catergory.data, private=form.private.data, playerCount=1,
                       isActive=True, hostID=1)  # IDK ABOUT HOST ID

        db.session.add(cr)
        db.session.commit()
    return render_template('create_room.html', title='Create Room', form=form)


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    return render_template('index.html', title='Home')
