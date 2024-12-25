import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import AddPatientForm, DeletePatientForm, LoginForm, RegistrationForm
from config import Config
from datetime import datetime

# Flask app setup
app = Flask(__name__)
app.config.from_object(Config)

# Database setup
db = SQLAlchemy(app)
Migrate(app, db)

# Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.template_filter('format_date')
def format_date(value):
    if isinstance(value, datetime):
        return value.strftime('%d-%m-%Y')
    return value

# Models
class Doctor(UserMixin, db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(user_id)

class Patient(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy=True)
    gender = db.Column(db.String(10), nullable=True)
    weight = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    blood_type = db.Column(db.String(3), nullable=True)
    dob = db.Column(db.String(10), nullable=False)

    def __init__(self, name, doctor_id, gender=None, weight=None, height=None, blood_type=None, dob=None):
        self.name = name
        self.doctor_id = doctor_id
        self.gender = gender
        self.weight = weight
        self.height = height
        self.blood_type = blood_type
        self.dob = dob
        
# EHR Medical Records!!!!
class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    medications = db.Column(db.Text, nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    vital_signs = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment_plan = db.Column(db.Text, nullable=True)
    chief_complaint = db.Column(db.Text, nullable=True)  # Reason for visit
    medical_history = db.Column(db.Text, nullable=True)  # Past medical history
    family_history = db.Column(db.Text, nullable=True)   # Hereditary conditions
    social_history = db.Column(db.Text, nullable=True)   # Lifestyle factors
    prognosis = db.Column(db.Text, nullable=True)        # Doctor's assessment of outcomes
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    def __init__(self, patient_id, medications=None, allergies=None, vital_signs=None, diagnosis=None, 
                 treatment_plan=None, chief_complaint=None, medical_history=None, family_history=None, 
                 social_history=None, prognosis=None):
        self.patient_id = patient_id
        self.medications = medications
        self.allergies = allergies
        self.vital_signs = vital_signs
        self.diagnosis = diagnosis
        self.treatment_plan = treatment_plan
        self.chief_complaint = chief_complaint
        self.medical_history = medical_history
        self.family_history = family_history
        self.social_history = social_history
        self.prognosis = prognosis
        




# Routes
@app.route('/')
def index():
    return render_template('home.html')
############################################################################################################

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        doctor = Doctor(username=form.username.data, password=hashed_password)
        db.session.add(doctor)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
############################################################################################################

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        doctor = Doctor.query.filter_by(username=form.username.data).first()
        if doctor and check_password_hash(doctor.password, form.password.data):
            login_user(doctor)
            flash("Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password. Try again.", "danger")
    return render_template('login.html', form=form)
############################################################################################################

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))
############################################################################################################

@app.route('/add-patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    form = AddPatientForm()
    if form.validate_on_submit():
        new_patient = Patient(
            name=form.name.data,
            doctor_id=current_user.id,  # Retrieve the doctor ID from the logged-in user
            gender=form.gender.data,
            weight=form.weight.data,
            height=form.height.data,
            blood_type=form.blood_type.data,
            dob = form.dob.data
            )
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient added successfully", "success")
        return redirect(url_for('list_patients'))
    return render_template('add.html', form=form)
############################################################################################################

@app.route('/list')
@login_required
def list_patients():
    patients = Patient.query.filter_by(doctor_id=current_user.id).all()
    return render_template('list.html', patients=patients)
############################################################################################################

@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete_patient():
    form = DeletePatientForm()
    if form.validate_on_submit():
        patient_id = form.id.data
        patient = Patient.query.filter_by(id=patient_id, doctor_id=current_user.id).first()
        if patient:
            db.session.delete(patient)
            db.session.commit()
            flash("Patient deleted successfully!", "success")
        else:
            flash("Patient not found or unauthorized action.", "danger")
        return redirect(url_for('list_patients'))
    return render_template('delete.html', form=form)
############################################################################################################

@app.route('/medical_records/<int:patient_id>')
@login_required
def medical_records(patient_id):
    # Ensure the patient belongs to the logged-in doctor
    patient = Patient.query.filter_by(id=patient_id, doctor_id=current_user.id).first_or_404()
    
    # Fetch all medical records for the patient
    records = MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()
    
    return render_template('medical_records.html', patient=patient, medical_records=records)

############################################################################################################

@app.route('/add_record/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_record(patient_id):
    # Ensure the patient belongs to the logged-in doctor
    patient = Patient.query.filter_by(id=patient_id, doctor_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        # Get form data
        medications = request.form.get('medications')
        allergies = request.form.get('allergies')
        vital_signs = request.form.get('vital_signs')
        diagnosis = request.form.get('diagnosis')
        treatment_plan = request.form.get('treatment_plan')
        chief_complaint = request.form.get('chief_complaint')
        medical_history = request.form.get('medical_history')
        family_history = request.form.get('family_history')
        social_history = request.form.get('social_history')
        prognosis = request.form.get('prognosis')

        # Validate required fields
        if not chief_complaint or not diagnosis:
            flash("Chief complaint and diagnosis are required fields.", "danger")
            return redirect(url_for('add_record', patient_id=patient_id))

        # Create and save the new record
        new_record = MedicalRecord(
            patient_id=patient_id,
            medications=medications,
            allergies=allergies,
            vital_signs=vital_signs,
            diagnosis=diagnosis,
            treatment_plan=treatment_plan,
            chief_complaint=chief_complaint,
            medical_history=medical_history,
            family_history=family_history,
            social_history=social_history,
            prognosis=prognosis
        )
        db.session.add(new_record)
        db.session.commit()
        flash("Medical record added successfully!", "success")
        return redirect(url_for('medical_records', patient_id=patient_id))
    
    return render_template('add_record.html', patient=patient)

############################################################################################################

@app.route('/edit_record/<int:record_id>', methods=['GET', 'POST'])
@login_required
def edit_record(record_id):
    # Fetch the record and ensure it belongs to the logged-in doctor
    record = MedicalRecord.query.get_or_404(record_id)
    if record.patient.doctor_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('list_patients'))
    
    if request.method == 'POST':
        # Update the record with form data
        record.medications = request.form.get('medications')
        record.allergies = request.form.get('allergies')
        record.vital_signs = request.form.get('vital_signs')
        record.diagnosis = request.form.get('diagnosis')
        record.treatment_plan = request.form.get('treatment_plan')
        record.chief_complaint = request.form.get('chief_complaint')
        record.medical_history = request.form.get('medical_history')
        record.family_history = request.form.get('family_history')
        record.social_history = request.form.get('social_history')
        record.prognosis = request.form.get('prognosis')

        # Commit changes to the database
        db.session.commit()
        flash("Medical record updated successfully!", "success")
        return redirect(url_for('medical_records', patient_id=record.patient_id))
    
    return render_template('edit_record.html', record=record)

############################################################################################################

@app.route('/patient/<int:patient_id>/basic-info', methods=['GET', 'POST'])
@login_required
def basic_info(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = AddPatientForm(obj=patient)
    if form.validate_on_submit():
        patient.gender = form.gender.data
        patient.weight = form.weight.data
        patient.height = form.height.data
        patient.blood_type = form.blood_type.data
        db.session.commit()
        flash('Basic information updated successfully!', 'success')
        return redirect(url_for('patient_list'))  # Adjust redirect as needed
    return render_template('basic_info.html', form=form, patient=patient)



############################################################################################################


@app.route('/confirm_delete_record/<int:record_id>', methods=['GET'])
@login_required
def confirm_delete_record_page(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if record.patient.doctor_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('list_patients'))
    
    return render_template('delete_record.html', record=record)
############################################################################################################

@app.route('/delete_record/<int:record_id>', methods=['POST'])
@login_required
def delete_record(record_id):
    record = MedicalRecord.query.get_or_404(record_id)
    if record.patient.doctor_id != current_user.id:
        flash("Unauthorized action or record not found.", "danger")
        return redirect(url_for('list_patients'))
    
    db.session.delete(record)
    db.session.commit()
    flash("Medical record deleted successfully.", "success")
    return redirect(url_for('medical_records', patient_id=record.patient_id))

if __name__ == '__main__':
    app.run(debug=True)
