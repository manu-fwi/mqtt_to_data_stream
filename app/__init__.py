from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app import config

config.config.load_config("config.txt")
#Start DB engine
engine = create_engine('sqlite:///app.db', echo=True)
models.Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine,expire_on_commit=False)
