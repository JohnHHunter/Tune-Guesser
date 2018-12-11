from flask import render_template, flash, redirect, url_for, request, Flask, jsonify
from app import app, db
from app.forms import LoginForm, RoomForm, RegistrationForm, JoinByCodeForm
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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html', title='Home')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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


@app.route('/guest', methods=['GET', 'POST'])
def guest():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    numbers = random.randint(100, 99999999)
    username = "Guest" + str(numbers)
    taken = player.query.filter_by(username=username).first()
    if taken:
        while taken:
            numbers = random.randint(100, 99999999)
            username = "Guest" + numbers
            taken = player.query.filter_by(username=username).first()
    user = player(username=username, registered=False, totalSongsPlayed=0,
                  totalCorrectGuesses=0, monthlySongsPlayed=0, monthlyCorrectGuesses=0)
    db.session.add(user)
    db.session.commit()
    flash('You have been logged in as a guest')
    curr_user = player.query.filter_by(username=username).first()
    login_user(curr_user, remember=False)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('home')
    return redirect(next_page)


@app.route('/home')
@login_required
def home():
    form = JoinByCodeForm()
    if form.validate_on_submit():
        room = game_room.query.filter_by(code=form.code.data).first()
        if room is None:
            flash("Room does not exist")
            return render_template('join.html', form=form, title='Join Room')
        db.session.add(current_user)
        db.session.commit()
        room.playerCount += 1
        return redirect(url_for('room_game', code=room.code))
    game_list = game_room.query.all()
    return render_template('home.html', title='Home', form=form, game_list=game_list)


@app.route('/leaderboard/all_time', methods=['GET', 'POST'])
def leaderboard():
    category = "Correct Guesses: All Time"
    next_right = 'leaderboard_monthly_correct'
    next_left = 'leaderboard_monthly_correct'
    players = player.query.all()
    list_size = 1
    top_correct_guesses = []
    players_on_leaderboard = []
    while list_size <= 10:
        top_score = 0
        top_player = player.query.filter_by(username='Nobody').first()
        for person in players:
            if (person.totalCorrectGuesses > top_score) and (person not in players_on_leaderboard):
                top_player = person
                top_score = person.totalCorrectGuesses
        players_on_leaderboard.append(top_player)
        player_to_add = str(list_size) + ". " + top_player.username + " - " + str(top_player.totalCorrectGuesses)
        top_correct_guesses.append(player_to_add)
        list_size += 1

    return render_template('leaderboard.html', next_left=next_left, next_right=next_right,
                           top_correct_guesses=top_correct_guesses, category=category, title='Home')


@app.route('/leaderboard/monthly', methods=['GET', 'POST'])
def leaderboard_monthly_correct():
    category = "Correct Guesses: This Month"
    next_right = 'leaderboard'
    next_left = 'leaderboard'
    players = player.query.all()
    list_size = 1
    top_correct_guesses = []
    players_on_leaderboard = []
    while list_size <= 10:
        top_score = 0
        top_player = player.query.filter_by(username='Nobody').first()
        for person in players:
            if (person.monthlyCorrectGuesses > top_score) and (person not in players_on_leaderboard):
                top_player = person
                top_score = person.monthlyCorrectGuesses
        players_on_leaderboard.append(top_player)
        player_to_add = str(list_size) + ". " + top_player.username + " - " + str(top_player.monthlyCorrectGuesses)
        top_correct_guesses.append(player_to_add)
        list_size += 1

    return render_template('leaderboard.html', next_left=next_left, next_right=next_right,
                           top_correct_guesses=top_correct_guesses, category=category, title='Home')


@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    form = RoomForm()
    form.category.choices = \
        [('Joji', 'Joji'), ('Rex Orange County', 'Rex Orange County'), ('The Gunpoets', 'The Gunpoets')]
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
    player_list = []
    song_link = "https://www.youtube.com/embed/iqztd7uMvVI"
    if game:
        ptg = player_to_game(playerID=current_user.id, gameRoomID=game.id, points=0)
        db.session.add(ptg)
        db.session.commit()
        players_in_game = player_to_game.query.filter_by(gameRoomID=game.id).all()
        for p in players_in_game:
            player_to_add = player.query.filter_by(id=p.playerID).first()
            if player_to_add not in player_list:
                player_list.append(player_to_add)
        all_songs = song.query.filter_by(artist=game.category).all()
        song_list = []
        for s in all_songs:
            song_list.append(s)
        curr_song = random.choice(song_list)
        song_id = curr_song.link
        song_id = song_id[32:]
        youtube = "https://www.youtube.com/embed/"
        link_end = "?start=" + str(curr_song.startTime) + "&autoplay=1"
        song_link = youtube + song_id + link_end
        return render_template('game_room.html', player_list=player_list, title=code, song_link=song_link, room=game,
                               current_user=current_user, hostID=game.hostID)
    return render_template('game_room.html', player_list=player_list, title=code, song_link=song_link, room=game)


@app.route('/_next_song')
def next_song(code):
    game = game_room.query.filter_by(code=code).first()
    all_songs = song.query.filter_by(artist=game.category).all()
    song_list = []
    for s in all_songs:
        song_list.append(s)
    curr_song = random.choice(song_list)
    song_id = curr_song.link
    song_id = song_id[32:]
    youtube = "https://www.youtube.com/embed/"
    link_end = "?start=" + str(curr_song.startTime) + "&autoplay=1"
    song_link = youtube + song_id + link_end
    return jsonify(song=song_link)


@app.route('/reset_db')
def reset_db():
    flash("Resetting database: deleting old data and repopulating with dummy data")
    # clear all data from all tables
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print('Clear table {}'.format(table))
        db.session.execute(table.delete())
    db.session.commit()

    songs = [
        # Joji
        song(
            id=1,
            artist='Joji',
            title="SLOW DANCING IN THE DARK",
            link="https://www.youtube.com/watch?v=K3Qzzggn--s",
            startTime=22),
        song(
            id=2,
            artist='Joji',
            title="TEST DRIVE",
            link="https://www.youtube.com/watch?v=PEBS2jbZce4",
            startTime=23),
        song(
            id=3,
            artist='Joji',
            title="XNXX",
            link="https://www.youtube.com/watch?v=iBUnToeuY18",
            startTime=22),

        # Rex Orange County
        song(
            id=4,
            artist='Rex Orange County',
            title="Sunflower",
            link="https://www.youtube.com/watch?v=Z9e7K6Hx_rY",
            startTime=48),
        song(
            id=5,
            artist='Rex Orange County',
            title="Loving is Easy",
            link="https://www.youtube.com/watch?v=39IU7ADaXmQ",
            startTime=65),
        song(
            id=6,
            artist='Rex Orange County',
            title="BEST FRIEND ",
            link="https://www.youtube.com/watch?v=OqBuXQLR4Y8",
            startTime=30),

        # The Gunpoets
        song(
            id=7,
            artist='The Gunpoets',
            title="Make You Happy",
            link="https://www.youtube.com/watch?v=XigvD9PSknk",
            startTime=14),
        song(
            id=8,
            artist='The Gunpoets',
            title="We Sing, We Dance",
            link="https://www.youtube.com/watch?v=1Q5HMoh6CB0",
            startTime=31),
        song(
            id=9,
            artist='The Gunpoets',
            title="8 Track Mind",
            link="https://www.youtube.com/watch?v=32iLMq01qi8",
            startTime=8),
    ]

    players = [
        player(id=1, username='Nobody', email='nobody@email.com', registered=False, totalSongsPlayed=0,
               totalCorrectGuesses=0, monthlySongsPlayed=0, monthlyCorrectGuesses=0),
        player(id=2, username='player0', email='player0@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=800, monthlySongsPlayed=500, monthlyCorrectGuesses=112),
        player(id=3, username='player1', email='player1@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=900, monthlySongsPlayed=500, monthlyCorrectGuesses=23),
        player(id=4, username='player2', email='player2@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=132, monthlySongsPlayed=500, monthlyCorrectGuesses=41),
        player(id=5, username='player3', email='player3@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=487, monthlySongsPlayed=500, monthlyCorrectGuesses=62),
        player(id=6, username='player4', email='player4@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=935, monthlySongsPlayed=500, monthlyCorrectGuesses=63),
        player(id=7, username='player5', email='player5@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=234, monthlySongsPlayed=500, monthlyCorrectGuesses=213),
        player(id=8, username='player6', email='player6@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=628, monthlySongsPlayed=500, monthlyCorrectGuesses=412),
        player(id=9, username='player7', email='player7@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=117, monthlySongsPlayed=500, monthlyCorrectGuesses=123),
        player(id=10, username='player8', email='player8@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=623, monthlySongsPlayed=500, monthlyCorrectGuesses=41),
        player(id=11, username='player9', email='player9@email.com', registered=True, totalSongsPlayed=1000,
               totalCorrectGuesses=623, monthlySongsPlayed=500, monthlyCorrectGuesses=349)
    ]

    for person in players:
        db.session.add(person)

    for music in songs:
        db.session.add(music)
    db.session.commit()
    return render_template('index.html', title='Home')
