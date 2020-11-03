from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Lerua(Base):
    __tablename__ = 'lerua'
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    link = Column(String(500), nullable=False)
    price = Column(Integer, nullable=True)
    photos = Column(String(500), nullable=False)
    feature = Column(Text, nullable=False)


if __name__ == '__main__':
    engine = create_engine('sqlite:///leruaDB.db', echo=True)
    Base.metadata.create_all(engine)
