VERSION = (1, 3, 4)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mmpy_bot.plugins.models import Base
from mmpy_bot import config

database_uri = config.DATABASE_URI

def get_version():
    return '.'.join(map(str, VERSION))

engine = create_engine(database_uri, connect_args={'check_same_thread': False}, echo = True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print "database done"