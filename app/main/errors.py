from flask import render_template
from . import main


# 404 页面处理视图函数
@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404  # 返回的第二个参数是状态码


# 400 页面处理视图函数
@main.app_errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


# 500 页面处理视图函数
@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# 403 页面处理视图函数
@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403