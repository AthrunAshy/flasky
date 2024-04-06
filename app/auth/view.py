from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required
from . import auth
from ..models import User
from .forms import LoginForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # 验证用户存在且密码正确
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)  # form.remember_me.data为 False，则下次需要重新登录，为 True 则通过 cookie 保存登录信息
            # 原 URL 保存在查询字符串的 next 参数中，可从 request.args 字典中读取
            next = request.args.get('next')
            # 若查询字符串中没有 next 参数，或者不是相对路径，则重定向到 index
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            # next 参数正常则重定向到目标URL
            return redirect(next)
        flash('Invalid email or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))