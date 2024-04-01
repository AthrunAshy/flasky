from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# Bootstrap 和 Moment 需要实例化
bootstrap = Bootstrap(app)
moment = Moment(app)

# 以 FlaskForm 为基类建立提交用户名的 NameForm
class NameForm(FlaskForm):
    # StringField SubmitField 导入后是公用的，可以直接用
    # validators=[DataRequired()] 用于检验提交的数据
    # 以上都是 flask_wtf 提供的功能
    name = StringField('Name',validators=[DataRequired()])
    submit = SubmitField('Submit')


# 404 页面处理视图函数
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # 返回的第二个参数是状态码


# 400 页面处理视图函数
@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


# 500 页面处理视图函数
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# 主页视图函数
@app.route('/', methods=['GET', 'POST'])  # 定义路由和方法
def index():
    name = None
    form = NameForm()
    # validate_on_submit 是 FlaskForm 提供的用于在提交表单时验证表单数据是否有效
    if form.validate_on_submit:
        name = form.name.data  # data 是表单中 name 字段当前的值
        form.name.data = ''
    return render_template('index.html', name=name, form=form)