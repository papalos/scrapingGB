from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)
    title = Column(String(10), nullable=True)
    ref = Column(String(300), nullable=False)
    date = Column(Date(), nullable=False)


if __name__ == '__main__':
    engine = create_engine('sqlite:///newsDB.db', echo=True)
    Base.metadata.create_all(engine)
