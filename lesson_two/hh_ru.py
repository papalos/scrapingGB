import pandas as pd
from bs4 import BeautifulSoup as bs
import requests as r
import re

# вакансия для поиска
vacancy = 'тракторист'

# основной список для формирования данных
ls = []
# залоговки для запроса, типа браузер
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

# ---------------- Ищем на суперджобе ------------------------------
domain = 'https://www.superjob.ru'
search = domain + '/vacancy/search'

# первый запрос для определения количества страниц
response = r.get(search, params={'keywords': vacancy, 'page': 1})
text = response.text

sp = bs(text, 'html.parser')
paginator = sp.find(attrs={'class': "_3zucV L1p51 undefined _1Fty7 _2tD21 _3SGgo"})

if paginator is None:
    raise Exception('Некорректный запрос!')

# собираем хтмл постранично
for i in range(2, int([i for i in paginator.children][-2].get_text())+1):
    response = r.get(search, params={'keywords': vacancy, 'page': i})
    text += response.text

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
        ls.append([vac, _min, _max, val, domain + ref, 'Superjob'])


# ------------------------ Ищем на hh ----------------------------------
domain = 'https://hh.ru'
search = domain + '/search/vacancy'

# первый запрос для определения количества страниц
response = r.get(search, params={'text': vacancy, 'search_field': 'name', 'page': 0}, headers=headers)
text = response.text

sp = bs(text, 'html.parser')
paginator = sp.find(attrs={'data-qa': 'pager-block'})

if paginator is None:
    raise Exception('Некорректный запрос!')

# собираем хтмл постранично
for i in range(1, int([i for i in paginator.children][-3].a.get_text())):
    response = r.get(search, params={'text': vacancy, 'search_field': 'name', 'page': i}, headers=headers)
    text += response.text

# парсим полученный хтмл
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
        ls.append([vac, _min, _max, val, ref, 'hh.ru'])


df = pd.DataFrame(ls, columns=['Vacancy', 'Min', 'Max', 'Val', 'Ref', 'Site'])
pd.set_option('display.max_columns', None)
print(df)
