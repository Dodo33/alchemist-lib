from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

#import sqlalchemy_utils

import configparser

import os



HOSTNAME = None
USERNAME = None
PASSWORD = None
DB_NAME = None
    
config = configparser.ConfigParser()
path = os.path.join(os.path.dirname(__file__), "..")
filename = config.read(path + "/config.ini")

sections = config.sections()

if "DATABASE" in sections:
    db_config = config["DATABASE"]
    
    HOSTNAME = db_config["hostname"]
    USERNAME = db_config["user"]
    PASSWORD = db_config["pass"]
    DB_NAME = db_config["db"]

#DATABASE_URI = "mysql+mysqlconnector://{}:{}@{}:3306/{}".format(USERNAME, PASSWORD, HOSTNAME, DB_NAME)
#Engine = create_engine(DATABASE_URI)

URI = "mysql+mysqlconnector://{}:{}@{}:3306".format(USERNAME, PASSWORD, HOSTNAME)
mysql_engine = create_engine(URI)

#https://stackoverflow.com/questions/6506578/how-to-create-a-new-database-using-sqlalchemy
#if not sqlalchemy_utils.database_exists(Engine.url):
#    sqlalchemy_utils.create_database(Engine.url)

mysql_engine.execute("CREATE DATABASE IF NOT EXISTS {};".format(DB_NAME))

DATABASE_URI = "mysql+mysqlconnector://{}:{}@{}:3306/{}".format(USERNAME, PASSWORD, HOSTNAME, DB_NAME)
Engine = create_engine(DATABASE_URI)

#https://stackoverflow.com/questions/3039567/sqlalchemy-detachedinstanceerror-with-regular-attribute-not-a-relation
session_factory = sessionmaker(bind = Engine, expire_on_commit = False)

#https://stackoverflow.com/questions/32328354/facing-issues-with-sqlalchemypostgresql-session-management
#http://docs.sqlalchemy.org/en/latest/orm/contextual.html
Session = scoped_session(session_factory)

Base = declarative_base()


