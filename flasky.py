import os
import click
# from flask_migrate import Migrate
# 从 app 文件夹导入其下__init__.py 中的 create_app, db
from app import create_app, db
# 从 app 文件夹导入其下 model.py 中的 User 和 Role 
from app.models import User, Role

# 创建应用实例
app = create_app()
# migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)