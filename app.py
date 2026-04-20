from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import re

app = Flask(__name__)
app.secret_key = 'voyagesync_secure_session_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///voyagesync.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

WORD_LIST = ['alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel', 'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray', 'yankee', 'zulu', 'apple', 'river', 'stone', 'cloud', 'flame', 'ocean', 'moon', 'star', 'sun', 'forest', 'mountain', 'valley', 'wind', 'storm', 'rain', 'snow', 'ice', 'fire', 'earth', 'metal', 'wood', 'water', 'gold', 'silver']

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    recovery_hash = db.Column(db.String(256), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100), nullable=False)
    departure = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time = db.Column(db.String(50), nullable=False)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    reference_number = db.Column(db.String(50), nullable=False)
    total_cost = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()
    if not Flight.query.first():
        f1 = Flight(airline="AeroRail Express", departure="NYC", destination="LON", price=450.00, time="08:00 AM")
        f2 = Flight(airline="NeonJet", departure="SFO", destination="TOK", price=890.00, time="11:30 PM")
        f3 = Flight(airline="Quantum Air", departure="LAX", destination="SYD", price=1200.00, time="02:15 PM")
        db.session.add_all([f1, f2, f3])
        db.session.commit()
    if not Hotel.query.first():
        h1 = Hotel(name="The Obsidian", location="LON", room_type="Suite", price_per_night=350.00)
        h2 = Hotel(name="Neon Lights Inn", location="TOK", room_type="Deluxe", price_per_night=280.00)
        h3 = Hotel(name="Teal Waters Resort", location="SYD", room_type="Villa", price_per_night=500.00)
        db.session.add_all([h1, h2, h3])
        db.session.commit()

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if password != confirm_password:
        flash('Passwords do not match. Please try again.', 'error')
        return redirect(url_for('index', modal='signup'))
    
    existing_username = User.query.filter_by(username=username).first()
    if existing_username:
        flash('That username is already taken. Please choose another one.', 'error')
        return redirect(url_for('index', modal='signup')) 

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('An account with that email already exists. Try logging in!', 'error')
        return redirect(url_for('index', modal='login')) 
        
    if len(password) < 8:
        flash('Security Alert: Password must be at least 8 characters long.', 'error')
        return redirect(url_for('index', modal='signup')) 
        
    if not re.search(r"[@%&$!*#?^]", password):
        flash('Security Alert: Password must contain at least one special character (e.g., @, %, &, $).', 'error')
        return redirect(url_for('index', modal='signup')) 
        
    phrase = " ".join(random.choices(WORD_LIST, k=10))
    phrase_hash = generate_password_hash(phrase, method='pbkdf2:sha256')
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    new_user = User(username=username, email=email, password_hash=hashed_password, recovery_hash=phrase_hash)
    db.session.add(new_user)
    db.session.commit()
    session['user_id'] = new_user.id
    
    flash(f'Account created! CRITICAL: Save this 10-word phrase: "{phrase}". You need it to reset your password later!', 'success')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        flash('Login successful. Welcome back!', 'success')
    else:
        flash('Invalid email or password. Please try again.', 'error')
        return redirect(url_for('index', modal='login')) 
        
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    phrase = request.form.get('phrase').strip().lower()
    new_password = request.form.get('new_password')
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.recovery_hash, phrase):
        if len(new_password) < 8:
            flash('Password reset failed: New password must be at least 8 characters long.', 'error')
            return redirect(url_for('index', modal='reset'))
            
        if not re.search(r"[@%&$!*#?^]", new_password):
            flash('Password reset failed: New password must contain a special character.', 'error')
            return redirect(url_for('index', modal='reset'))

        user.password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
        flash('Password successfully reset! You can now log in with your new password.', 'success')
    else:
        flash('Reset failed. Ensure your 10-word phrase is typed exactly.', 'error')
        return redirect(url_for('index', modal='reset'))
        
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user = User.query.get(session['user_id'])
    if user:
        Booking.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        db.session.commit()
        session.pop('user_id', None)
        flash('Your account and all associated data have been permanently deleted.', 'success')
        
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/flights')
def flights():
    all_flights = Flight.query.all()
    return render_template('flights.html', flights=all_flights)

@app.route('/hotels')
def hotels():
    all_hotels = Hotel.query.all()
    return render_template('hotels.html', hotels=all_hotels)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    item_id = request.form.get('item_id')
    item_type = request.form.get('item_type')
    price = request.form.get('total_price')
    if item_type == 'flight':
        item = Flight.query.get(item_id)
    else:
        item = Hotel.query.get(item_id)
    return render_template('checkout.html', item=item, item_type=item_type, price=price)

@app.route('/confirmation', methods=['POST'])
def confirmation():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    item_type = request.form.get('item_type')
    total_cost = float(request.form.get('total_price'))
    ref_num = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    new_booking = Booking(user_id=session['user_id'], type=item_type, reference_number=ref_num, total_cost=total_cost)
    db.session.add(new_booking)
    db.session.commit()
    return render_template('confirmation.html', ref_num=ref_num, total_cost=total_cost)

if __name__ == '__main__':
    app.run(debug=True)