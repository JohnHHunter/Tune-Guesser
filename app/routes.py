from flask import render_template
from app import app


@app.route('/')
def index():
    return render_template('index.html', title='Home')


@app.route('/register')
def register():
    return render_template('register.html', title='Register')


@app.route('/login')
def login():
    return render_template('login.html', title='Register')
