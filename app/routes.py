from flask import render_template
from app import app, db
from app.forms import LoginForm, RoomForm
from app. models import Player, PlayerToGame, GameRoom, Song, SongToGame, ChatMessage


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
    return render_template('leaderboard.html', title='Home')

@app.route('/create_room')
def create_room():
    form = RoomForm()
    if form.validate_on_submit():
        cr = GameRoom(name=form.name.data, category= form.catergory.data, private= form.private.data, playerCount= 1,
                      isActive= True, hostID=# IDK )

        db.session.add(cr)
        db.session.commit()
    return render_template('create_room.html', title='Home')
