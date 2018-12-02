from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RoomForm, RegistrationForm
from app.models import player, player_to_game, game_room, song, song_to_game, chat_message
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
import string
import random
from datetime import datetime


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = player(username=form.username.data, email=form.email.data, registered=True, totalSongsPlayed=0,
                      totalCorrectGuesses=0, monthlySongsPlayed=0, monthlyCorrectGuesses=0)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form, title='Register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = player.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.html', form=form, title='Sign In')


@app.route('/home')
@login_required
def home():
    game_list = game_room.query.all()
    return render_template('home.html', title='Home', game_list=game_list)


@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():  # trying to get one last thing to work
    players = player.query.all()
    list_size = 1
    top_correct_guesses = []
    players_on_leaderboard = []
    while list_size <= 10:
        top_score = 0
        for person in players:
            if (person.totalCorrectGuesses > top_score) and (person not in players_on_leaderboard):
                top_player = person
                top_score = person.totalCorrectGuesses
        players_on_leaderboard.append(top_player)
        player_to_add = str(list_size) + ". " + top_player.username + " - " + str(top_player.totalCorrectGuesses)
        top_correct_guesses.append(player_to_add)
        list_size += 1

    return render_template('leaderboard.html', top_correct_guesses=top_correct_guesses, title='Home')


@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        # Code generator
        chars = string.ascii_uppercase + string.digits
        size = 4
        # Check to see if code exists
        while True:
            code = ''.join(random.choice(chars) for _ in range(size))
            rooms_with_code = game_room.query.filter_by(code=code).all()
            if not rooms_with_code:
                break
        cr = game_room(name=form.name.data, hostID=current_user.id, playerCount=1, category=form.category.data,
                       isActive=True, code=code, created=datetime.utcnow(), updated=datetime.utcnow(),
                       private=form.private.data)
        db.session.add(cr)
        db.session.commit()
        return redirect(url_for("room_game", code=code))
    return render_template('create_room.html', title='Create Room', form=form)


@app.route('/<code>', methods=['GET', 'POST'])
@login_required
def room_game(code):
    game = game_room.query.filter_by(code=code).first()
    return render_template('game_room.html', title=code, room=game)


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    players = [
        player(id=1, username='player0', email='player0@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=800, monthlySongsPlayed=500, monthlyCorrectGuesses=112),
        player(id=2, username='player1', email='player1@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=900, monthlySongsPlayed=500, monthlyCorrectGuesses=23),
        player(id=3, username='player2', email='player2@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=132, monthlySongsPlayed=500, monthlyCorrectGuesses=41),
        player(id=4, username='player3', email='player3@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=487, monthlySongsPlayed=500, monthlyCorrectGuesses=62),
        player(id=5, username='player4', email='player4@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=935, monthlySongsPlayed=500, monthlyCorrectGuesses=63),
        player(id=6, username='player5', email='player5@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=234, monthlySongsPlayed=500, monthlyCorrectGuesses=213),
        player(id=7, username='player6', email='player6@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=628, monthlySongsPlayed=500, monthlyCorrectGuesses=412),
        player(id=8, username='player7', email='player7@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=117, monthlySongsPlayed=500, monthlyCorrectGuesses=123),
        player(id=9, username='player8', email='player8@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=623, monthlySongsPlayed=500, monthlyCorrectGuesses=41),
        player(id=10, username='player9', email='player9@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=623, monthlySongsPlayed=500, monthlyCorrectGuesses=349)
    ]

    for person in players:
        db.session.add(person)
    db.session.commit()

    return render_template('index.html', title='Home')
