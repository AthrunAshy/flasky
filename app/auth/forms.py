from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    # type=password 的 <input>
    password = PasswordField('Password', validators=[DataRequired()])
    # 复选框
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')