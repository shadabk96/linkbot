VERSION = (1, 3, 4)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from linkbot.plugins.link_models import Base
from linkbot import config

database_uri = config.DATABASE_URI

def get_version():
    return '.'.join(map(str, VERSION))

engine = create_engine(database_uri, connect_args={'check_same_thread': False}, echo = False)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

print "--> Database Created Successfully"