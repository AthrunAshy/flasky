import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    # 测试起始
    def setUp(self):
        self.app = create_app('testing')
        # 创建上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        # 建立测试数据库
        db.create_all()

    # 测试结束
    def tearDown(self):
        # 删除测试数据库
        db.session.remove()
        db.drop_all()
        # 关闭上下文
        self.app_context.pop()
        
    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])