import os

from flask import Flask, Blueprint

import config
from applications.view import init_view
from common import register_api
from common.flask_uploads import configure_uploads
from common.utils.upload import photos
from extensions import init_plugs

api_bp: Blueprint = Blueprint('api', __name__, url_prefix='/api/v1')

from .rights import register_rights_api
from .system import register_sys_api
from .users import register_users_api

register_rights_api(api_bp)
register_users_api(api_bp)
register_sys_api(api_bp)


def init_api(app: Flask) -> None:
    app.register_blueprint(api_bp)


def create_app() -> Flask:
    app = Flask('pear-admin-flask')

    # 引入数据库配置
    app.config.from_object(config)

    # 注册各种插件
    init_plugs(app)

    # 注册路由
    init_view(app)

    # 注册接口（restful api）
    init_api(app)

    # 文件上传
    configure_uploads(app, photos)

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        logo()

    return app


def logo():
    print('''
 _____                              _           _         ______ _           _    
|  __ \                    /\      | |         (_)       |  ____| |         | |   
| |__) |__  __ _ _ __     /  \   __| |_ __ ___  _ _ __   | |__  | | __ _ ___| | __
|  ___/ _ \/ _` | '__|   / /\ \ / _` | '_ ` _ \| | '_ \  |  __| | |/ _` / __| |/ /
| |  |  __/ (_| | |     / ____ \ (_| | | | | | | | | | | | |    | | (_| \__ \   < 
|_|   \___|\__,_|_|    /_/    \_\__,_|_| |_| |_|_|_| |_| |_|    |_|\__,_|___/_|\_\\

    ''')
