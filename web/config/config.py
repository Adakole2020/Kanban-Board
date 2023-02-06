import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = "kanban"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///taskStorage.db"
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'test@gmail.com'
    MAIL_PASSWORD = 'test123'
    DEBUG = False
    TESTING = False
    

class DevConfig(Config):
    DEBUG = True
    
class TestConfig(Config):
    TESTING = True
    DEBUG = True
    WTF_CSRF_METHODS = False
    
    
class ProdConfig(Config):
    pass