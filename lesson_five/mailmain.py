from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from time import sleep as slp
import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from modelMail import Mail, Base


def get_link(elements):
    links = []
    for el in elements:
        links.append(el.get_attribute('href'))
    return links

# Попробовал сгенерировать код из SeleniumIDE.
# он его адаптирует по pytest, много излишних действий, селекторы чаще заданы неоднозначно процентов 90 пришлось переписать


# Не знаю какой драйвер использует SeleniumIDE но рекомендовано было установить geckodriver
# проблемы с ним описаны ниже
driver = webdriver.Firefox(executable_path=r'E:\gbMetodiSbora\lesson1\lesson_five\geckodriver.exe')
driver.set_window_size(1244, 832)
driver.get("https://account.mail.ru")
login = WebDriverWait(driver, 50).until(
  EC.presence_of_element_located((By.NAME, "username"))
)
login.send_keys("study.ai_172@mail.ru")
driver.find_element(By.TAG_NAME, "button").click()
password = WebDriverWait(driver, 50).until(
  EC.presence_of_element_located((By.NAME, "password"))
)
password.send_keys("NextPassword172")
driver.find_element(By.TAG_NAME, "button").click()

slp(3)
elements = driver.find_elements(By.CLASS_NAME, "llc")
links = get_link(elements)
last_elem = elements[-1]
# предложенный вариант скроклинга через ActionChains.move_to_element()
# по всей видимости не работает для драйвера geckodriver
# ибо он просто выполняет фокусировку на этом элементе (как я понял)
# и при попытке переместиться к последнему элементу списка вылетает ошибка,
# что фокус вышел за границы окна скролинга при этом не происходит
# использовать js с помощью driver.execute_script() для целей скролинга у меня тоже не вышло
# благо раскопал на просторах интернет инфу о существовании ниже расположенного свойства (сначала пытался вызвать его как метод, потом посмотрел реализацию)
last_elem.location_once_scrolled_into_view
while True:
    slp(2)
    more_elements = driver.find_elements(By.CLASS_NAME, "llc")
    # надеюсь, что это можно считать корректным завершением скролинга
    if last_elem == more_elements[-1]:
        break
    last_elem = more_elements[-1]
    links += get_link(more_elements)
    last_elem.location_once_scrolled_into_view

# Не поулчилось по-человечески собрать все ссылки со страницы, после скролинга в выборку попадают чуть больше 20 штук
# не пойму почему так происходит, может драйвер собирает только видимоые объекты
# при попытке обратиться к первым элементам вываливается ошибка об отсутствии элемента на страницы, в браузере видно, что ссылки не подгружаются а обновляются при скролинге
links = set(links)
mouth = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
driver.get(list(links)[5])
slp(5)

engine = create_engine('sqlite:///mailDB.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

for i in links:
    print(i)
    driver.get(i)
    slp(3)
    title = driver.find_element(By.TAG_NAME, 'h2').text
    fr = driver.find_element(By.CLASS_NAME, 'letter-contact').text
    d = driver.find_element(By.CLASS_NAME, 'letter__date').text.split(',')[0].split(' ')
    if len(d) == 3:
        dt = datetime.date(int(d[2]), mouth.index(d[1]) + 1, int(d[0]))
    elif len(d) == 2:
        dt = datetime.date(datetime.datetime.today().year, mouth.index(d[1]) + 1, int(d[0]))
    else:
        dt = datetime.datetime.today()
    text = str(driver.find_element(By.CLASS_NAME, 'letter__body').text)
    mail = Mail(m_from=fr, date=dt, title=title, text=text)
    session.add(mail)
    try:
        session.commit()
    except IntegrityError:
        print('Что-то пошло не так!')
        pass
session.close()
