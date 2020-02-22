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
        return "<Link(author='%s', message='%s', link='%s', channel='%s', timestamp='%s')>" % (self.author, self.message, self.link, self.channel, self.timestamp)


# link1 = Link(author = "shadab", message = "message", link = "www.google.com", channel = "general", timestamp="1234")

# session.add(link1)

# session.commit()

# session.query(Link).filter(Link.author.in_(['shadab'])).all()

