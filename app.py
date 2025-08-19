from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@hostname:port/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(20), nullable=False)
    cns = db.Column(db.String(20), nullable=True)
    priority = db.Column(db.String(20), nullable=True)
    restrictions = db.Column(db.String(200), nullable=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date_out = db.Column(db.DateTime, nullable=False)
    date_back = db.Column(db.DateTime, nullable=True)
    vehicle = db.Column(db.String(50), nullable=True)
    driver = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='Agendada')

@app.route('/') 
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.check_password(request.form['password']):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Usuário ou senha inválidos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    patients = Patient.query.all()
    trips = Trip.query.all()
    return render_template('dashboard.html', patients=patients, trips=trips)

@app.route('/patients/new', methods=['GET','POST'])
def new_patient():
    if request.method == 'POST':
        patient = Patient(
            name=request.form['name'],
            cpf=request.form['cpf'],
            cns=request.form['cns'],
            priority=request.form['priority'],
            restrictions=request.form['restrictions']
        )
        db.session.add(patient)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_patient.html')

@app.route('/trips/new', methods=['GET','POST'])
def new_trip():
    patients = Patient.query.all()
    if request.method == 'POST':
        trip = Trip(
            patient_id=request.form['patient_id'],
            destination=request.form['destination'],
            date_out=datetime.strptime(request.form['date_out'],'%Y-%m-%d'),
            date_back=datetime.strptime(request.form['date_back'],'%Y-%m-%d') if request.form['date_back'] else None,
            vehicle=request.form['vehicle'],
            driver=request.form['driver'],
            status=request.form['status']
        )
        db.session.add(trip)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('new_trip.html', patients=patients)

if __name__ == '__main__':
    app.run(debug=True)
