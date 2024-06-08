from flask import Flask, render_template, jsonify, request, redirect
from model import Session, User
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session = Session()
        data = request.form
        user = session.query(User).filter_by(user_name=data.get('username')).first()
        if user:
            passwordReader = PasswordHasher()
            try:
                passwordReader.verify(user.password, data.get('password'))
                return redirect('/home')
            except VerifyMismatchError:
                return render_template('login.html', error='Invalid credentials')
        else:
            return render_template('login.html', error='Invalid credentials')
    else:
        return render_template('login.html')

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        session = Session()
        data = request.form
        password_writer = PasswordHasher()
        hashed_password = password_writer.hash(data.get('password'))
        user = User(
            user_name=data.get('username'),
            password=hashed_password,
        )
        session.add(user)
        session.commit()
        return redirect('/login')
    else:
        return render_template('register.html')

@app.route("/mark_attendance", methods = ["POST"])
def mark_attendance():
    pass

@app.route("/dashboard")
def display_dashboard():
    pass