import json
from sqlalchemy import  Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import  declarative_base, relationship

Base = declarative_base()

def to_json(inst, cls):
    convert = dict()
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to convert using " + str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return d

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship('Post', backref='user', lazy='dynamic')
    maxStreak = Column(Integer)
    maxPostperDay = Column(Integer)


    def __repr__(self):
        return f"<User {self.id}: {self.name}>"

    @property
    def json(self):
        return to_json(self, self.__class__)

# Association table
post_tag_association = Table(
    'post_tag',
    Base.metadata,
    Column('post_id', String, ForeignKey('post.id'), primary_key=True),
    Column('tag_id', String, ForeignKey('tag.name'), primary_key=True)
)

class Post(Base):
    __tablename__ = 'post'
    id = Column(String, primary_key=True)
    title = Column(String)
    type = Column(String)
    upVoteCounts = Column(Integer)
    downVoteCounts = Column(Integer)
    commentsCounts = Column(Integer)
    category = Column(String)
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    tags = relationship('Tag', secondary=post_tag_association, back_populates='posts')

    def __repr__(self):
        return f"<Post {self.title}>"

    @property
    def json(self):
        return to_json(self, self.__class__)

class Tag(Base):
    __tablename__ = 'tag'
    name = Column(String, primary_key=True)
    posts = relationship('Post', secondary=post_tag_association, back_populates='tags')

    def __repr__(self):
        return f"<Tag {self.name}>"

    @property
    def json(self):
        return to_json(self, self.__class__)

class ReadDoc(Base):
    __tablename__ = 'readdoc'
    docName = Column(String, primary_key=True)
    duplicateUser = Column(Integer)
    duplicatePost = Column(Integer)

    def __repr__(self):
        return f"<ReadDoc {self.docName}>"

    @property
    def json(self):
        return to_json(self, self.__class__)
