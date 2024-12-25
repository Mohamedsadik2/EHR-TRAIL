from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, FloatField, DateField, DecimalField, SelectField
from wtforms.validators import DataRequired, EqualTo, Optional, Length

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class AddPatientForm(FlaskForm):
    name = StringField('Patient Name', validators=[DataRequired()])
    gender = StringField('Gender', validators=[Optional(), Length(max=10)])
    weight = FloatField('Weight (kg)', validators=[Optional()])
    height = FloatField('Height (cm)', validators=[Optional()])
    blood_type = StringField('Blood Type', validators=[Optional(), Length(max=3)])
    dob = DateField('Date of Birth', format='%d-%m-%Y', validators=[Optional(), Length(max=10)])
    submit = SubmitField('Add Patient')

class DeletePatientForm(FlaskForm):
    id = IntegerField('Patient ID to Remove', validators=[DataRequired()])
    submit = SubmitField('Delete Patient')

class AddMedicalRecordForm(FlaskForm):
    details = StringField('Record Details', validators=[DataRequired()])
    submit = SubmitField('Add Record')

