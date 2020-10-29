# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
# --------- sqlalchemy --------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from modelVacancy import Vacancy, Base


class JobparserPipeline:
    def __init__(self):
        engine = create_engine('sqlite:///vDB.db', echo=True)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def process_item(self, item, spider):
        ooo = item['item_salary']
        if spider.name == 'hhru':
            if ooo[0] == 'от ':
                _min = int(''.join(ooo[1].split('\xa0')))
                _max = None
                val = ''.join(ooo[-2].split('\xa0'))
            elif ooo[0] == 'до ':
                _min = None
                _max = int(''.join(ooo[1].split('\xa0')))
                val = ''.join(ooo[-2].split('\xa0'))
            elif ooo[0] == 'По договорённости' or ooo[0] == 'з/п не указана':
                _min = None
                _max = None
                val = None
            else:
                oo = ooo[0].split('-')
                _min = int(''.join(oo[0].split('\xa0')))
                _max = int(''.join(oo[1].split('\xa0')))
                val = ''.join(ooo[-2].split('\xa0'))
            print(_min, _max, val)
        else:
            ooo = item['item_salary']
            if ooo[0] == 'от':
                oo = ooo[2].split('\xa0')
                _min = int(oo[0] + oo[1])
                _max = None
                val = oo[-1]
            elif ooo[0] == 'до':
                oo = ooo[2].split('\xa0')
                _min = None
                _max = int(oo[0] + oo[1])
                val = oo[-1]
            elif ooo[0] == 'По договорённости':
                _min = None
                _max = None
                val = None
            elif len(ooo) < 4:
                _min = int(''.join((ooo[0].split('\xa0'))))
                _max = int(''.join((ooo[0].split('\xa0'))))
                val = ooo[-1]
            else:
                _min = int(''.join((ooo[0].split('\xa0'))))
                _max = int(''.join((ooo[1].split('\xa0'))))
                val = ooo[-1]
            print('Цена', _min, _max, val)
        new_vacancy = Vacancy(
            vacancy=item['item_name'],
            salaryMin=_min,
            salaryMax=_max,
            valuta=val,
            ref=item['item_url'],
            site=spider.name
        )
        try:
            self.session.add(new_vacancy)
            self.session.commit()
        except IntegrityError:
            print('Такая вакансия уже есть в Базе Данных!')
            self.session.rollback()

    def __del__(self):
        self.session.close()
