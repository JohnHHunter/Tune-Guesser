from flask import render_template
from app import app
from app.forms import LoginForm


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
