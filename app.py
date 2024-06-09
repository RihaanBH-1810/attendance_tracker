from flask import Flask, render_template, jsonify, request, redirect, session as flask_session
from model import Session, User
import bcrypt
import dummy_data as dData
from attendance import generateSSID, verify_ssid

app = Flask(__name__)
app.secret_key = "b'6y[^\xb2*|\xf2\xccd\x9d\x04'" # Remove this later

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/home")
def home():
    dummy_data = dData.dummy_data()
    if 'username' in flask_session:
        return render_template('home.html', username=flask_session['username'], records=dummy_data)
    return redirect('/login')

@app.route("/dashboard")
def dashboard():
    session = Session()
    current_user = session.query(User).filter_by(user_name=flask_session['username']).first()
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

    if not username or not password:
        return render_template('register.html', error='Username and password are required')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    shared_secret = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8')  # Generate a random shared secret
    new_user = User(
        user_name=username,
        password=hashed_password,
        current_day_labtime=0,
        labtime_data={},
        shared_secret=shared_secret  # Store the shared secret
    )
    session.add(new_user)
    session.commit()
    return redirect('/login')
else:
    return render_template('register.html')


@app.route("/logout")
def logout():
    flask_session.pop('username', None)
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
        new_mac_address = data.get('mac')
        
        if new_name:
            current_user.name = new_name
        
        if new_roll_no:
            current_user.rollNo = new_roll_no
        
        if new_mac_address:
            current_user.mac = new_mac_address

        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return render_template('dashboard.html', user=current_user, error=str(e))
        
        return redirect('/home')

    return render_template('edit_profile.html', user=current_user)

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    ssid_list = data.get('list')
    now = datetime.now()
    # hmac_shared_key = 
    # hmac_message =  data.get('hmac_message')
    # hmac_verfied =  False 
    authenticated = False 
    ssid_verified = False 

    session = Session()
    try:
        user = session.query(User).filter_by(user_name=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            authenticated = True
        ssid_verified = verify_ssid(ssid_list)
        if authenticated and ssid_verified:
            #update attendance here 
            pass

        





if __name__ == "__main__":
    app.run(debug=True)
