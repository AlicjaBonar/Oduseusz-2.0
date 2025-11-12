from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class TravelRegistrationForm(FlaskForm):
    first_name = StringField("Imię", validators=[DataRequired(), Length(min=2, max=50)])
    last_name = StringField("Nazwisko", validators=[DataRequired(), Length(min=2, max=50)])
    pesel = StringField("PESEL", validators=[DataRequired(), Length(min=11, max=11)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    country = StringField("Kraj", validators=[DataRequired()])
    city = StringField("Miasto", validators=[DataRequired()])
    submit = SubmitField("Zarejestruj podróż")