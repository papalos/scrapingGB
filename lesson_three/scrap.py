from bs4 import BeautifulSoup as bs
import requests as r
import re
# --------- sqlalchemy --------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from modelDB import Vacancy, Base


class Scraper:

    def __init__(self, vacancy):
        # вакансия для поиска
        self._vacancy = vacancy
        # основной список для формирования данных
        self._ls = []
        # залоговки для запроса, типа браузер
        self._headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

    def get_superjob_text(self):
        # ---------------- Ищем на суперджобе ------------------------------
        # метод возрвращает текст со всех страниц по искомой вакансии

        domain = 'https://www.superjob.ru'
        search = domain + '/vacancy/search'

        # первый запрос для определения количества страниц
        response = r.get(search, params={'keywords': self._vacancy, 'page': 1})
        text = response.text

        sp = bs(text, 'html.parser')
        paginator = sp.find(attrs={'class': "_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo"})

        if paginator is None:
            raise Exception('Некорректный запрос!')

        # собираем хтмл постранично
        for i in range(2, int([i for i in paginator.children][-2].get_text())+1):
            response = r.get(search, params={'keywords': self._vacancy, 'page': i})
            text += response.text
        return text

    def superjob_parse(self, text):
        # метод парсит принятый текст с сайта суперджоб и возвращает итератор с вакансиями

        domain = 'https://www.superjob.ru'

        # парсим полученный хтмл
        soup = bs(text, 'html.parser')

        # забираем все div-ы со страницы
        listV = soup.find_all(attrs={'class': "_2g1F-"})
        for i in listV:
            # среди них находим содержащие вакансии
            v = i.find(attrs={'class': re.compile("_2JivQ _1UJAN")})

            # из них достаем данные
            if v:
                vac = v.get_text()
                ref = v['href']
                ooo = i.find(attrs={'class': '_3mfro _2Wp8I PlM3e _2JVkc _2VHxz'}).get_text().split('\xa0')
                if ooo[0] == 'от':
                    _min = int(ooo[1] + ooo[2])
                    _max = None
                    val = ooo[-1]
                elif ooo[0] == 'до':
                    _min = None
                    _max = int(ooo[1] + ooo[2])
                    val = ooo[-1]
                elif ooo[0] == 'По договорённости':
                    _min = None
                    _max = None
                    val = None
                elif len(ooo) < 4:
                    _min = int(ooo[0] + ooo[1])
                    _max = int(ooo[0] + ooo[1])
                    val = ooo[-1]
                else:
                    _min = int(ooo[0] + ooo[1])
                    _max = int(ooo[3] + ooo[4])
                    val = ooo[-1]
                yield [vac, _min, _max, val, domain + ref, 'Superjob']

    def get_hh_text(self):
        # ------------------------ Ищем на hh ----------------------------------
        # метод возрвращает текст со всех страниц по искомой вакансии
        domain = 'https://hh.ru'
        search = domain + '/search/vacancy'

        # первый запрос для определения количества страниц
        response = r.get(search, params={'text': self._vacancy, 'search_field': 'name', 'page': 0}, headers=self._headers)
        text = response.text

        sp = bs(text, 'html.parser')
        paginator = sp.find(attrs={'data-qa': 'pager-block'})

        if paginator is None:
            raise Exception('Некорректный запрос!')

        # собираем хтмл постранично
        for i in range(1, int([i for i in paginator.children][-3].a.get_text())):
            response = r.get(search, params={'text': self._vacancy, 'search_field': 'name', 'page': i}, headers=self._headers)
            text += response.text
        return text

    def hh_parse(self, text):
        # метод парсит принятый текст с сайта ХХ и возвращает итератор с вакансиями

        soup = bs(text, 'html.parser')

        # забираем все div-ы со страницы
        listV = soup.find_all(attrs={'class': "vacancy-serp-item__row vacancy-serp-item__row_header"})

        for i in listV:
            # среди них находим содержащие вакансии
            v = i.find(attrs={'class': 'g-user-content'}).a
            c = i.find(attrs={'data-qa': "vacancy-serp__vacancy-compensation"})

            # из них достаем данные
            if v and c:
                vac = v.get_text()
                ref = v['href']
                ooo = c.get_text().split(' ')
                if ooo[0] == 'от':
                    _min = int(''.join(ooo[1].split('\xa0')))
                    _max = None
                    val = ''.join(ooo[-1].split('\xa0'))
                elif ooo[0] == 'до':
                    _min = None
                    _max = int(''.join(ooo[1].split('\xa0')))
                    val = ''.join(ooo[-1].split('\xa0'))
                elif ooo[0] == 'По договорённости':
                    _min = None
                    _max = None
                    val = None
                else:
                    oo = ooo[0].split('-')
                    _min = int(''.join(oo[0].split('\xa0')))
                    _max = int(''.join(oo[1].split('\xa0')))
                    val = ''.join(ooo[-1].split('\xa0'))
                yield [vac, _min, _max, val, ref, 'hh.ru']

    def add_new_vacancy(self, iterator_vacancy):
        # паринемает итератор с вакансиями и поэлементно добавляет их БД отсеивая дубликаты
        # поиск дубликатов выполен средствами БД - проверка поля на уникальность

        engine = create_engine('sqlite:///vacancyDB.db', echo=True)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        for vacancy in iterator_vacancy:
            new_vacancy = Vacancy(
                vacancy=vacancy[0],
                salaryMin=vacancy[1],
                salaryMax=vacancy[2],
                valuta=vacancy[3],
                ref=vacancy[4],
                site=vacancy[5]
            )
            try:
                session.add(new_vacancy)
                session.commit()
            except IntegrityError:
                print('Такая вакансия уже есть в Базе Данных!')
                session.rollback()
        session.close()

    def salary_greater_than(self, salary):
        engine = create_engine('sqlite:///vacancyDB.db', echo=True)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        return session.query(Vacancy.vacancy, Vacancy.ref).filter((Vacancy.salaryMin > salary) | (Vacancy.salaryMax > salary)).all()



