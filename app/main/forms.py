from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


# 以 FlaskForm 为基类建立提交用户名的 NameForm
class NameForm(FlaskForm):
    # StringField SubmitField 导入后是公用的，可以直接用
    # validators=[DataRequired()] 用于检验提交的数据
    # 以上都是 flask_wtf 提供的功能
    name = StringField('Name',validators=[DataRequired()])
    submit = SubmitField('Submit')