from functools import wraps  # 保留原函数的元信息
from flask import abort  # 用于返回HTTP错误响应
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    def decorator(f):  # 接收原函数作为参数
        @wraps(f)  # 保留原函数的元信息
        def decorated_function(*args, **kwargs):  # 接收任意参数
            # 如果当前用户没有权限访问，则返回HTTP 403 Forbidden响应
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function  # 返回装饰后的函数
    return decorator  # 返回装饰器


def admin_required(f):
    return permission_required(Permission.ADMIN)(f)