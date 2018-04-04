from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_uploads import UploadSet, configure_uploads, patch_request_class, TEXT, DEFAULTS, IMAGES
from .create_user_table import Task

import os,sys
pkg_path = os.path.sep.join(
    (os.path.abspath(os.curdir).split(os.path.sep)[:-1]))
# print pkg_path
if pkg_path not in sys.path:
    sys.path.append(pkg_path)

from ipcs.task import add,non_certify
from ipcs.redis_api import get_remote_handler,get_local_handler
from misc import get_host_ip

# print add.name,non_certify.name

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
ufile = UploadSet('report')

def create_rpc_client():
    rpc_client = {}
    rpc_client['merchant'] = non_certify
    rpc_client['add'] = add
    return rpc_client

def create_task_client():
    task_client = Task()
    task_client.create_table()
    return task_client
    
def create_app(config_name):

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    configure_uploads(app, ufile)
    
    #create rpc client
    rpc_client = create_rpc_client()
    setattr(app, 'rpc_client', rpc_client)

    #create mysql client
    task_client = create_task_client()
    setattr(app,'task_column_names',task_client.get_column_names(task_client.table_struct))
    setattr(app,'task_client',task_client)
    
    #create redis client
#     if get_host_ip() == '120.24.189.82':
#         redis_client = get_remote_handler()
#     else:
#         redis_client = get_local_handler()
    
    redis_client = get_local_handler()
    setattr(app,'redis_client',redis_client)
    return app

xapp = create_app(os.getenv('FLASK_CONFIG') or 'default')
