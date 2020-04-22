from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt import JWT
from os import environ
from flask_mail import Mail

db = SQLAlchemy()
sendgrid_api_key = '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'

# administrator list
ADMINS_FROM_EMAIL_ADDRESS = ['aboy.gabriel@outlook.com']
mail = Mail()
def create_app():
    # Todo: Make this handle environment configs better
    app = Flask(__name__)
    app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
    app.config["SECRET_KEY"] = "thisshouldbesetforproduction"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"  # url
    app.config["JWT_AUTH_URL_RULE"] = "/api/auth/login"
    app.config["JWT_SECRET_KEY"] = "thisshouldbesetforproduction"

    # Email configuration
    app.config.update(dict(
        DEBUG = True,
        MAIL_SERVER = 'smtp.sendgrid.net',
        MAIL_PORT = 465,
        MAIL_USE_TLS = False,
        MAIL_USE_SSL = True,
        MAIL_USERNAME = 'apikey',
        # API key should be env variable
        MAIL_PASSWORD = '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',
    ))

    CORS(app)
    

    from .models import User, track, trackout, wavFile
    from .routes.auth import authentication_handler, identity_handler
    JWT(app, authentication_handler, identity_handler)

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

    from .routes.wavfiles import wavfiles_bp
    app.register_blueprint(wavfiles_bp)

    from .routes.errors import errors_bp
    app.register_blueprint(errors_bp)

    return app
