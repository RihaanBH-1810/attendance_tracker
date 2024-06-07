from flask import Flask, render_template, jsonify, request
from models import Session, User

app = Flask(__name__)

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/add_user", methods = ['POST'])
def add_user():
    ession = Session()
    data = request.json
    user = User(
        user_name=data.get('user_name'),
        password=data.get('password'),
        daily_labtime=data.get('daily_lab_time', 0),  
        labtime_data=data.get('uptime_data', {}) 
    )
    session.add(user)
    session.commit()
    return jsonify({'message': 'User added successfully'}), 201


@app.route("/register")
def register():
    return render_template('register.html')

@app.route("/mark_attendance", methods = ["POST"])
def mark_attendance:
    pass 

@app.route("/dashboard")
def display_dashboard:
    pass 

