from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Mail(Base):
    __tablename__ = 'mail'
    id = Column(Integer, primary_key=True)
    m_from = Column(String(50), nullable=False)
    date = Column(Date(), nullable=False)
    title = Column(String(10), nullable=True)
    text = Column(String(300), nullable=False)



if __name__ == '__main__':
    engine = create_engine('sqlite:///mailDB.db', echo=True)
    Base.metadata.create_all(engine)
