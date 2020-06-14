import os

from flask import Flask
from App.views import sd,admin
from .exts import init_exts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



def create_app():
    static_floder = os.path.join(BASE_DIR, 'static')
    template_folder = os.path.join(BASE_DIR, 'templates')
    app = Flask(__name__, static_folder=static_floder, template_folder=template_folder)

    app.config['SECRET_KEY'] = '123'

    # 配置数据库
    DB_URI = 'mysql+pymysql://root:root@localhost:3306/shudong'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 注册蓝图
    app.register_blueprint(blueprint=sd)
    app.register_blueprint(blueprint=admin)
    # 初始化插件
    init_exts(app)

    return app
