from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine


Base = declarative_base()


class Vacancy(Base):
    __tablename__ = 'vacancy'
    __table_args__ = (UniqueConstraint('ref'), )
    id = Column(Integer, primary_key=True)
    vacancy = Column(String(50), nullable=False)
    salaryMin = Column(Integer, nullable=True)
    salaryMax = Column(Integer, nullable=True)
    valuta = Column(String(10), nullable=True)
    ref = Column(String(300), nullable=False)
    site = Column(String(25), nullable=False)


if __name__ == '__main__':
    engine = create_engine('sqlite:///vacancyDB.db', echo=True)
    Base.metadata.create_all(engine)
