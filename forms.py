from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_wtf import FlaskForm

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})

    password = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login", render_kw={"class": "btn btn-success"})

class AddPlanForm(FlaskForm):
    header = StringField(validators=[InputRequired(), Length(
        min=1, max=20)], render_kw={"placeholder": "Header"})
    description = TextAreaField(validators=[Length(min=0, max=100)], render_kw={
        "placeholder": "Description",
        "cols": "25",
        "rows": "6"})
    importance = RadioField("Plan importance", choices=[
        ("not important", "not important"),
        ("important", "important"),
        ("very important", "very important"),
    ], render_kw={"class": "radio-field"})
    submit = SubmitField("Plan", render_kw={"class": "btn btn-success"})