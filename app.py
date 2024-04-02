import os

from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 将当前脚本的相对路径转为绝对路径保存到 basedir 
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Bootstrap 和 Moment 需要实例化
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'  # 指定表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  # unique 表示表内任意两个name不能重复
    def __repr__(self):
        return '<Role %r>' % self.name
    users = db.relationship('User', backref='role', lazy='dynamic')

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  # index=True在创建表时自动在该列上创建索引，这对于涉及按用户名搜索用户或根据用户名列进行筛选的查询非常有用。
    def __repr__(self):  # 如果有一个名为 user 的 User 类的实例，其 username 为'john'，那么调用user.__repr__()将返回 <User 'john'>
        return '<User %r>' % self.username
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


# 以 FlaskForm 为基类建立提交用户名的 NameForm
class NameForm(FlaskForm):
    # StringField SubmitField 导入后是公用的，可以直接用
    # validators=[DataRequired()] 用于检验提交的数据
    # 以上都是 flask_wtf 提供的功能
    name = StringField('Name',validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


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
    form = NameForm()
    # validate_on_submit 是 FlaskForm 提供的用于在提交表单时验证表单数据是否有效
    if form.validate_on_submit:
        user = User.query.filter_by(username=form.name.data).first()  # 检查表单中的 name 和数据库中的 name 是否有重复
        if user is None:
            user = form.name.data
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))


