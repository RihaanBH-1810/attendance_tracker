from flask import Flask, render_template, jsonify, request, redirect
from model import Session, User
import bcrypt

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
            if bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
                return redirect('/home')
            else:
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
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return render_template('register.html', error='Username and password are required')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(
            user_name=username,
            password=hashed_password,
            current_day_labtime=0,
            labtime_data={},
        )
        session.add(new_user)
        session.commit()
        return redirect('/login')
    else:
        return render_template('register.html')

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    pass

@app.route("/dashboard")
def display_dashboard():
    pass

if __name__ == "__main__":
    app.run(debug=True)
