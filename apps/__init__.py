from flask import Flask
from . import gps_analyze, dog_face_recognition, cat_face_recognition
#from flask_sqlalchemy import SQLAlchemy
#from database import db
#from database import create_db

#db = SQLAlchemy()

def create_app():


    app = Flask(__name__)


    #config
    config = app.config.get('ENV')
    if config == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')

    app.register_blueprint(gps_analyze.app_gps)
    app.register_blueprint(dog_face_recognition.recognition_dog)
    app.register_blueprint(cat_face_recognition.recognition_cat)

    app.config.from_object(config)

    #db.init_app(app)
    #with app.app_context():
    #    db.create_all()

    #conn = create_db(app.config.get('SQLALCHEMY_DATABASE_URI'))
    return app