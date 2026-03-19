import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta
from flask import Flask

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__,
                instance_relative_config=True,
                template_folder='templates',
                static_folder='../static')

    try:
        from config import config
        app.config.from_object(config[config_name])
    except ImportError:
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(32).hex())
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
        app.config['WHID_ENABLED'] = True
        app.config['WHID_FORCE_LOGOUT_PREVIOUS'] = True

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder

    log_folder = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_folder, exist_ok=True)

    if not app.debug:
        file_handler = RotatingFileHandler(
            os.path.join(log_folder, 'oxyx.log'), maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    from app.auth import init_auth_routes
    init_auth_routes(app)

    from app.main import init_main_routes
    init_main_routes(app)

    from app.admin import init_admin_routes
    init_admin_routes(app)

    return app
