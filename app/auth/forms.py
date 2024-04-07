from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    # type=password 的 <input>
    password = PasswordField('Password', validators=[DataRequired()])
    # 复选框
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    # regexp 正则表达式验证: 必须以字母开头，只能包含字母、数字、点、下划线
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, numbers, dots or underscores')])
    password = PasswordField(
        'Password', validators=[DataRequired(), EqualTo('password2', message='Passwords must match.')])
    # 确认密码
    password2 = PasswordField(
        'Confirm password', validators=[DataRequired()])
    # 注册按钮
    submit = SubmitField('Register')

    # 验证邮箱是否已注册
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    # 验证用户名是否已注册
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')