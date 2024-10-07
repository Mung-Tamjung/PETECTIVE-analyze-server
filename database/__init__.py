#from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine
from config import DevelopmentConfig
from sqlalchemy.ext.declarative import declarative_base


#class Base(DeclarativeBase):
#    pass

#db=SQLAlchemy(model_class=Base)

#def create_db(url):
#    engine = create_engine(url, encoding = "utf8")
#    conn = engine.connect()
#    return conn

SQLALCHEMY_DATABASE_URL = DevelopmentConfig.SQLALCHEMY_DATABASE_URI
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Base = declarative_base()

