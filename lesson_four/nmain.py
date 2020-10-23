from scrapN import NewsGetter as NG
from datetime import datetime
# --------- sqlalchemy --------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from modelNews import News, Base


a = NG()
ls_mail = a.get_mailru()
ls_lenta = a.get_lenta()
ls_yandex = a.get_yandex()

engine = create_engine('sqlite:///newsDB.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
for n in ls_mail + ls_lenta + ls_yandex:
    news = News(source=n[0], title=n[1], ref=n[2], date=datetime.strptime(n[3], "%Y-%m-%d"))
    session.add(news)
try:
    session.commit()
except IntegrityError:
    print('Что-то пошло не так!')
    pass
session.close()

