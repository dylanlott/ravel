from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt import JWT
from os import environ
from flask_mail import Mail
from api.queueWorker import Q, Job, worker

from flaskthreads import AppContextThread
from datetime import timedelta
import logging
import sys
from logging.handlers import RotatingFileHandler
db = SQLAlchemy()



# administrator list - must be from domain confirmed with SendGrid
ADMINS_FROM_EMAIL_ADDRESS = ['robot@ravelmusic.io']
mail = Mail()


def create_app():
    # Todo: Make this handle environment configs better
    app = Flask(__name__)
    app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
    app.config["SECRET_KEY"] = "thisshouldbesetforproduction"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"  # url
    app.config["JWT_AUTH_URL_RULE"] = "/api/auth/login"
    app.config["JWT_SECRET_KEY"] = "thisshouldbesetforproduction"
    app.config["JWT_EXPIRATION_DELTA"] = timedelta(days=1)

    # app.config['SQLALCHEMY_ECHO'] = True
    # Email configuration
    app.config.update(dict(
        DEBUG=True,
        MAIL_SERVER='smtp.sendgrid.net',
        MAIL_PORT=465,
        MAIL_USE_TLS=False,
        MAIL_USE_SSL=True,
        MAIL_USERNAME='apikey',
        MAIL_PASSWORD=environ.get("SENDGRID_API_KEY"),
        MAIL_DEBUG=False,
    ))
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    from .models import User
    from .models.track_models import TrackOut, Track, Equalizer, Compressor, Deesser, Reverb
    from .routes.auth import authentication_handler, identity_handler
    JWT(app, authentication_handler, identity_handler)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root.addHandler(handler)

    '''
        # db.drop_all()
        # db.create_all() only creates models within scope
    '''
    with app.app_context():
        mail.init_app(app)
        db.init_app(app)
        # db.drop_all()
        db.create_all()
        db.session.commit()
        AppContextThread(target=worker, daemon=True).start()

    '''
    WebServer Rendering Routes
    '''
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    '''
    Database Interactive Routes
    '''
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes.users import users_bp
    app.register_blueprint(users_bp)

    from .routes.tracks import tracks_bp
    app.register_blueprint(tracks_bp)

    from .routes.trackOuts import trackouts_bp
    app.register_blueprint(trackouts_bp)

    from .routes.errors import errors_bp
    app.register_blueprint(errors_bp)

    return app
