from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app import config
from app.config import log
import sys

#first load config file (only argument possible on the command line)
if len(sys.argv)==2:
    #load config
    log("trying to load config file: "+sys.argv[1])
    config.config.load_config(sys.argv[1])
else:
    #no argument or too many, try default config file
    config.config.load_config("config.txt")

    #Start DB engine
engine = create_engine('sqlite:///app.db', echo=True)
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine,expire_on_commit=False)
