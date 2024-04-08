from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


# 将current_user的权限信息注入到模板中
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)