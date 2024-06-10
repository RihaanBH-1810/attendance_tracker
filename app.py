from flask import Flask, render_template, jsonify, request, redirect, session as flask_session
from model import Session, User, Log
import bcrypt, json
from datetime import datetime, timedelta
from attendance import ssid_utils, hmac_utils
import os, base64
from sqlalchemy.exc import SQLAlchemyError
from config import config
from sqlalchemy.exc import SQLAlchemyError
import pytz

app = Flask(__name__)
app.secret_key = "b'6y[^\xb2*|\xf2\xccd\x9d\x04'"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    if 'username' in flask_session:
        session = Session()
        current_user = session.query(User).filter_by(user_name=flask_session['username']).first()
        

        print(f"Current User: {current_user}")

        attendance_records = session.query(Log).filter_by(member_id=current_user.id).all()
        

        print(f"Attendance Records: {attendance_records}")

        records = []
        for record in attendance_records:
            print(f"Record: {record}, Sessions: {record.sessions}")

            if isinstance(record.sessions, list):
                for session_data in record.sessions:
                    if isinstance(session_data, dict) and 'startTime' in session_data and 'endTime' in session_data:
                        records.append({
                            'name': current_user.name,
                            'rollNo': current_user.rollNo,
                            'date': record.date.strftime('%Y-%m-%d'),
                            'login_time': session_data.get('startTime'),
                            'logout_time': session_data.get('endTime')
                        })
                    else:
                        print(f"Invalid session data: {session_data}")
            else:
                print(f"Invalid sessions type: {type(record.sessions)}")


        print(f"Processed Records: {records}")

        session.close()
        return render_template('home.html', username=flask_session['username'], records=records)
    return redirect('/login')


@app.route("/dashboard")
def dashboard():
    session = Session()
    try:
        current_user = session.query(User).filter_by(user_name=flask_session['username']).first()
    except Exception as e:
        return redirect('/login')
    if 'username' in flask_session:
        return render_template('dashboard.html', username=flask_session['username'], user=current_user)
    return redirect('/login')

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session = Session()
        data = request.form
        user = session.query(User).filter_by(user_name=data.get('username')).first()
        if user and bcrypt.checkpw(data.get('password').encode('utf-8'), user.password.encode('utf-8')):
            flask_session['username'] = user.user_name
            return redirect('/home')
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
        name = data.get('name')
        rollNo = data.get('rollNo')

        if not username or not password or not name or not rollNo:
            return render_template('register.html', error='All fields are required')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        shared_secret = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')
        new_user = User(
            user_name=username,
            password=hashed_password,
            current_day_labtime=0,
            labtime_data=json.dumps({}),
            name=name,
            rollNo=rollNo,
            shared_secret=shared_secret
        )
        session.add(new_user)
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            return render_template('register.html', error='Username already exists')
        return redirect('/login')
    else:
        return render_template('register.html')

@app.route("/logout")
def logout():
    flask_session.clear()
    return redirect('/login')

@app.route("/editProfile", methods=['POST', 'GET'])
def edit_profile():
    if 'username' not in flask_session:
        return redirect('/login')

    session = Session()
    current_user = session.query(User).filter_by(user_name=flask_session['username']).first()

    if request.method == 'POST':
        data = request.form
        new_name = data.get('name')
        new_roll_no = data.get('rollNum')

        if new_name:
            current_user.name = new_name

        if new_roll_no:
            current_user.rollNo = new_roll_no

        print(current_user.shared_secret)

        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            return render_template('dashboard.html', user=current_user, error=str(e))

        return redirect('/home')

    return render_template('dashboard.html', user=current_user)

@app.route("/verify", methods=["POST"])
def verify_credentials():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    shared_secret = data.get('shared_secret')

    session = Session()
    try:
        user = session.query(User).filter_by(user_name=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')) and user.shared_secret == shared_secret:
            return jsonify({"status": "success", "message" : "Creds Verified"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
    except Exception as e:
        print("Error occurred:", e)
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    ssid_list = data.get('list')
    message = data.get('message')
    received_hmac = data.get('hmac')
    to_tz = pytz.timezone(str(config['TIMEZONE']))  
    now = datetime.now(to_tz)  
    authenticated = False
    ssid_verified = False

    session = Session()
    try:
        user = session.query(User).filter_by(user_name=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            authenticated = True
        ssid_verified = ssid_utils.verify_ssid(ssid_list)

        if authenticated and ssid_verified and hmac_utils.verify_hmac(user.shared_secret, message, received_hmac):
            log = session.query(Log).filter(Log.member_id == user.id, Log.date == now.date()).first()

        if not log:
            log = Log(member_id=user.id, date=now, lastSeen=now, duration=0, sessions=[])
            session.add(log)
            user.current_day_labtime = 0

            labtime_data = json.loads(user.labtime_data)
            labtime_data[str(now.date())] = []
            user.labtime_data = json.dumps(labtime_data)

            session.commit()

        if log.lastSeen.tzinfo is None:
            log.lastSeen = to_tz.localize(log.lastSeen)
            time_change = now - log.lastSeen
            log.duration += time_change.total_seconds()
            user.current_day_labtime += time_change.total_seconds()
            log.lastSeen = now
            labtime_data = json.loads(user.labtime_data)
            sessions = labtime_data[str(now.date())]
            sessions.append({'startTime': (now - time_change).isoformat(), 'endTime': now.isoformat()})
            labtime_data[str(now.date())] = sessions
            user.labtime_data = json.dumps(labtime_data)
            session.commit()
            return jsonify({"status": "success"}), 200

        else:
            return jsonify({"status": "error"}), 401
    except Exception as e:
        print("Error occurred:", e)
        session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)
