from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os
from dotenv import load_dotenv
import web.config.config as configModule

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class = configModule.DevConfig()):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()
    db.init_app(app)
    
    with app.app_context():
        db.drop_all()
        db.create_all()
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    from web.users.routes import users
    from web.main.routes import main
    from web.boards.routes import boards
    
    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(boards)

    return app