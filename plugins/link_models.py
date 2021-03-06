from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key = True)
    author = Column(String)
    message = Column(String)
    link = Column(String)
    channel = Column(String)
    timestamp = Column(String)

    def __repr__(self):
        return "<Link(id='%d', author='%s', message='%s', link='%s', channel='%s', timestamp='%s')>" % (self.id, self.author, self.message, self.link, self.channel, self.timestamp)

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key = True)
    message_id = Column(Integer)
    tag = Column(String)

    def __repr__(self):
        return "<Tag(message_id='%d', tag='%s')>" % (self.message_id, self.tag)

class BotSubscriber(Base):
    __tablename__ = 'bot_subcriber'

    id = Column(Integer, primary_key = True)
    user_id = Column(String)
    team_id = Column(String)
    channel_id = Column(String)

    def __repr__(self):
        return "<BotSubcriber(user_id='%s', team_id='%s', channel_id='%s')>" % (self.user_id, self.team_id, self.channel_id)

# link1 = Link(author = "shadab", message = "message", link = "www.google.com", channel = "general", timestamp="1234")

# session.add(link1)

# session.commit()

# session.query(Link).filter(Link.author.in_(['shadab'])).all()

