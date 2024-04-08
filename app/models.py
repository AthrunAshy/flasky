from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_required, AnonymousUserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
from flask import current_app
from . import db, login_manager

# 权限常量，若想为一个用户角色赋予权限，使其能够关注其他用户，
# 并在文章中发表评论，则权限值为 FOLLOW + COMMENT = 3
class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'  # 指定表名
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)  # unique 表示表内任意两个name不能重复
    default = db.Column(db.Boolean, default=False, index=True)  # default 表示默认角色
    permissions = db.Column(db.Integer)  # 角色的权限
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    # 定义 __init__ 方法，在创建 Role 实例时，自动为其添加默认权限
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm
    
    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm
    
    def reset_permissions(self):
        self.permissions = 0
    
    # 检查角色是否具有某种权限，即参数 perm 是否在角色的权限列表中
    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    def __repr__(self):
        return '<Role %r>' % self.name
    

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)  # index=True在创建表时自动在该列上创建索引，这对于涉及按用户名搜索用户或根据用户名列进行筛选的查询非常有用。
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))  # 数据库中存的不能是明文密码，得是经过哈希的散列值
    confirmed = db.Column(db.Boolean, default=False)  # 确认邮件，默认值为 False

    # 定义 __init__ 方法，在创建 User 实例时，自动为其添加默认角色，若用户的 email 与 FLASKY_ADMIN 相同，则自动赋予管理员角色
    def __init__(self, **kwargs):
        # 调用父类的 __init__ 方法，以便为实例设置属性
        super(User, self).__init__(**kwargs)
        # 如果用户的 email 与 FLASKY_ADMIN 相同，则自动赋予管理员角色
        if self.email == current_app.config['FLASKY_ADMIN']:
            self.role = Role.query.filter_by(permissions=Permission.ADMIN).first()
        # 如果没有指定角色，则赋予默认角色
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()
    
    # 被 @property 装饰器修饰后，可以直接像访问属性一样使用(User.password)，而不需要显式调用方法
    @property 
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter  # 用于定义 password 属性的 setter 方法，允许给 password 属性赋值，以更新用户密码
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):  # 验证密码是否正确
        return check_password_hash(self.password_hash, password)
        
    def generate_confirmation_token(self, expiration=3600):  # 生成确认邮件的 token
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')
    
    def confirm(self, token):  # 验证 token 并确认用户
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        # 如果 token 有效，则将 confirmed 字段设置为 True
        self.confirmed = True
        db.session.add(self)
        return True
    
    def generate_reset_token(self, expiration=3600):  # 生成重置密码的 token
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')
    
    # 使用 @staticmethod 装饰器定义的类方法，不需要实例化类就可以调用，可以直接通过类名调用，如 User.reset_password(token, new_password)
    @staticmethod
    def reset_password(token, new_password):  # 验证 token 并重置密码
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))  # 根据 token 找到用户
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True
    
    def generate_email_change_token(self, new_email, expiration=3600):  # 生成修改邮箱的 token
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email}).decode('utf-8')
    
    def change_email(self, token):  # 验证 token 并修改邮箱
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True
    
    def can(self, perm):  # 检查用户是否具有某种权限，即参数 perm 是否在用户的角色的权限列表中
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):  # 检查用户是否为管理员
        return self.can(Permission.ADMIN)

    def __repr__(self):  # 如果有一个名为 user 的 User 类的实例，其 username 为'john'，那么调用user.__repr__()将返回 <User 'john'>
        return '<User %r>' % self.username


# 自定义匿名用户类，用于未登录的用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
    
login_manager.anonymous_user = AnonymousUser


# 注册用户登录后，Flask-Login 会调用 load_user 方法，把用户 ID 作为参数传入，返回一个 User 对象。
# 然后 Flask-Login 会把这个 User 对象存储在当前会话中，以便在后续请求中使用。
# 因此，在视图函数中，可以用 current_user 来获取当前登录的用户，并检查其权限。
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))