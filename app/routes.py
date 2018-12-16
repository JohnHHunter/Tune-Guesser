from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db, socketio
from app.forms import LoginForm, RoomForm, RegistrationForm, JoinByCodeForm
from app.models import player, game_room, song
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask_socketio import SocketIO, send
import string
import json
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
                      totalCorrectGuesses=0, monthlySongsPlayed=0, monthlyCorrectGuesses=0, roomID=0, pointsInRoom=0)
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
            return redirect(url_for('home'))
        db.session.add(current_user)
        db.session.commit()
        room.playerCount += 1
        return redirect(url_for('room_game', code=room.code))
    all_games = game_room.query.all()
    game_list = []
    for game in all_games:
        if game.playerCount < 8:
            game_list.append(game)
    return render_template('home.html', title='Home', form=form, game_list=game_list, current_user=current_user)


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
        cr = game_room(hostID=current_user.id, playerCount=0, category=form.category.data,
                       isActive=False, code=code, created=datetime.utcnow(), updated=datetime.utcnow(),
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
    song_link = ""
    if game:
        if game.playerCount >= 8:
            flash("Room is full")
            return redirect(url_for("home"))
        current_user.roomID = game.id
        current_user.pointsInRoom = 0
        current_user.hasGuessed = False
        db.session.commit()
        players_in_game = player.query.filter_by(roomID=game.id).all()
        for p in players_in_game:
            player_list.append(p)
        game.playerCount = len(player_list)
        db.session.commit()
        return render_template('game_room.html', player_list=player_list, title=code, room=game,
                               current_user=current_user, hostID=game.hostID, song_link=song_link)
    flash("Room does not exist")
    return redirect(url_for("home"))


@app.route('/_update')
def update():
    player_list = []
    game = game_room.query.filter_by(id=current_user.roomID).first()
    user = current_user.id
    if game:
        started = game.isActive
        players_in_game = player.query.filter_by(roomID=game.id).all()
        for p in players_in_game:
            player_list.append(p)
        game.playerCount = len(player_list)
        return jsonify(players=[p.serialize() for p in player_list], started=started, user=user)


@app.route('/_sync_song')
def sync_song():
    game = game_room.query.filter_by(id=current_user.roomID).first()
    curr_song = song.query.filter_by(title=game.current_song).first()
    if curr_song:
        song_id = curr_song.link[32:]
        youtube = "https://www.youtube.com/embed/"
        link_end = "?autoplay=1&showinfo=0&controls=0&amp;" + "start=" + str(curr_song.startTime)
        song_link = youtube + song_id + link_end
        return jsonify(result=song_link)


@app.route('/_next_song', methods=['GET', 'POST'])
def next_song():
    current_user.totalSongsPlayed += 1
    code = request.args.get('code', "")
    game = game_room.query.filter_by(code=code).first()
    current_user.hasGuessed = False
    if game:
        game.isActive = True
        all_songs = song.query.filter_by(artist=game.category).all()
        song_list = []
        for s in all_songs:
            song_list.append(s)
        curr_song = random.choice(song_list)
        song_id = curr_song.link
        song_id = song_id[32:]
        youtube = "https://www.youtube.com/embed/"
        link_end = "?autoplay=1&showinfo=0&controls=0&amp;" + "start=" + str(curr_song.startTime)
        song_link = youtube + song_id + link_end
        game.current_song = song_link
        game.current_song = curr_song.title
        db.session.commit()
        return jsonify(result=song_link, song_name=curr_song.title)
    return jsonify(result="none")


# Chat
@socketio.on('message')
def handle_message(msg):
    if current_user.is_authenticated:
        sender = current_user.username
        current_room = game_room.query.filter_by(id=current_user.roomID).first()
        if current_room.isActive:  # if game has started
            if msg.lower() == current_room.current_song.lower():  # check to see if message is correct answer
                if not current_user.hasGuessed:
                    whole_message = sender + " has guessed the song!"
                    send(whole_message, broadcast=True)
                    current_user.hasGuessed = True
                    current_user.pointsInRoom += 10
                    current_user.totalCorrectGuesses += 1
                    current_user.monthlyCorrectGuesses += 1
                    db.session.commit()
            else:
                whole_message = sender + ": " + msg
                send(whole_message, broadcast=True)
        else:
            whole_message = sender + ": " + msg
            send(whole_message, broadcast=True)


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
            id=4,
            artist='Joji',
            title="ATTENTION",
            link="https://www.youtube.com/watch?v=ulMHhPHYCi0",
            startTime=31),
        song(
            id=5,
            artist='Joji',
            title="WANTED U",
            link="https://www.youtube.com/watch?v=z9gVoelEjws",
            startTime=15),
        song(
            id=6,
            artist='Joji',
            title="CAN'T GET OVER YOU",
            link="https://www.youtube.com/watch?v=zbxAB7rTpDc",
            startTime=70),
        song(
            id=7,
            artist='Joji',
            title="YEAH RIGHT",
            link="https://www.youtube.com/watch?v=tG7wLK4aAOE",
            startTime=21),
        song(
            id=8,
            artist='Joji',
            title="NO FUN",
            link="https://www.youtube.com/watch?v=8Vlej7QUGGE",
            startTime=19),
        song(
            id=9,
            artist='Joji',
            title="COME THRU",
            link="https://www.youtube.com/watch?v=7QrEkeXZJLg",
            startTime=50),
        song(
            id=10,
            artist='Joji',
            title="will he",
            link="https://www.youtube.com/watch?v=R2zXxQHBpd8",
            startTime=37),

        # Rex Orange County
        song(
            id=11,
            artist='Rex Orange County',
            title="Sunflower",
            link="https://www.youtube.com/watch?v=Z9e7K6Hx_rY",
            startTime=48),
        song(
            id=12,
            artist='Rex Orange County',
            title="Loving is Easy",
            link="https://www.youtube.com/watch?v=39IU7ADaXmQ",
            startTime=65),
        song(
            id=13,
            artist='Rex Orange County',
            title="BEST FRIEND",
            link="https://www.youtube.com/watch?v=OqBuXQLR4Y8",
            startTime=30),
        song(
            id=14,
            artist='Rex Orange County',
            title="Corduroy Dreams",
            link="https://www.youtube.com/watch?v=oSl7I8ue400",
            startTime=19),
        song(
            id=15,
            artist='Rex Orange County',
            title="Untitled",
            link="https://www.youtube.com/watch?v=Z4lMPWXhAr8",
            startTime=1),

        # The Gunpoets
        song(
            id=16,
            artist='The Gunpoets',
            title="Make You Happy",
            link="https://www.youtube.com/watch?v=XigvD9PSknk",
            startTime=14),
        song(
            id=17,
            artist='The Gunpoets',
            title="We Sing, We Dance",
            link="https://www.youtube.com/watch?v=1Q5HMoh6CB0",
            startTime=31),
        song(
            id=18,
            artist='The Gunpoets',
            title="8 Track Mind",
            link="https://www.youtube.com/watch?v=32iLMq01qi8",
            startTime=8),
        song(
            id=19,
            artist='The Gunpoets',
            title="In the Dark",
            link="https://www.youtube.com/watch?v=OeU2qocZ9Lc",
            startTime=14),
        song(
            id=20,
            artist='The Gunpoets',
            title="Action, Cameras, Lights",
            link="https://www.youtube.com/watch?v=oYSgFOqvZ9g",
            startTime=8),
        song(
            id=21,
            artist='The Gunpoets',
            title="Beautiful People",
            link="https://www.youtube.com/watch?v=eBAO9cANYe0",
            startTime=22),
    ]

    players = [
        player(id=1, username='Nobody', email='nobody@email.com', registered=False, totalSongsPlayed=0,
               totalCorrectGuesses=0, monthlySongsPlayed=0, monthlyCorrectGuesses=0)
    ]

    for person in players:
        db.session.add(person)

    for music in songs:
        db.session.add(music)
    db.session.commit()
    return render_template('index.html', title='Home')
