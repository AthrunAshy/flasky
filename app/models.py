from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class Role(db.Model):
    __tablename__ = 'roles'  # 指定表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  # unique 表示表内任意两个name不能重复
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)  # index=True在创建表时自动在该列上创建索引，这对于涉及按用户名搜索用户或根据用户名列进行筛选的查询非常有用。
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))  # 数据库中存的不能是明文密码，得是经过哈希的散列值

    def __repr__(self):  # 如果有一个名为 user 的 User 类的实例，其 username 为'john'，那么调用user.__repr__()将返回 <User 'john'>
        return '<User %r>' % self.username
    
    @property  # 将字段转化为只写属性
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter  # 用于定义 password 属性的 setter 方法，允许给 password 属性赋值，以更新用户密码
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):  # 验证密码是否正确
        return check_password_hash(self.password_hash, password)