import requests as r
from lxml import html
from datetime import datetime


class NewsGetter:
    def __init__(self):
        self._month = ['января', 'февраля', 'марта', 'апреля', 'майя', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        # залоговки для запроса, типа браузер
        self._headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Cache-Control': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'
        }

    def get_mailru(self):
        l = []
        main_link = 'https://news.mail.ru/'
        response = r.get(main_link, headers=self._headers)
        root = html.fromstring(response.text)
        block = root.xpath('((//div[@class="wrapper"]//div[@class="js-module"]))//a/@href')
        for i in block:
            ref = i
            news = r.get(i, headers=self._headers)
            newstext = html.fromstring(news.text)
            article = newstext.xpath('(//div[contains(@class, "article")])')[0]
            title = article.xpath('.//h1/text()')[0]
            dateN = article.xpath('.//span[@datetime]/@datetime')[0].split('T')[0]
            source = article.xpath('.//span[@class="link__text"]/text()')[0]
            l.append([source, title, ref, dateN])
        return l

    def get_lenta(self):
        l = []
        main_link = 'https://lenta.ru'
        response = r.get(main_link, headers=self._headers)
        root = html.fromstring(response.text)
        main_news = root.xpath('//section[contains(@class, "b-top7-for-main")]//a')
        for i in main_news:
            dateN = i.xpath('./time/@title')
            if dateN:
                # если есть более легкий путь конвертации дат, подскажите пожалуйста
                d = dateN[0].split(' ')
                dt = '-'.join((d[2], str(self._month.index(d[1])+1), d[0]))
                source = 'Лента'
                title = i.xpath('./text()')[0].replace('\xa0', ' ')
                ref = i.xpath('./@href')[0]
                if ref.find('http') == -1:
                    ref = main_link + ref
                l.append([source, title, ref, dt])
        return l

    def get_yandex(self):
        l = []
        main_link = 'https://yandex.ru/news'
        response = r.get(main_link, headers=self._headers)
        root = html.fromstring(response.text)
        articles = root.xpath('//article')
        for art in articles:
            dataN = float(art.xpath('.//a/@data-log-id')[0].split('-')[1])
            dt = datetime.utcfromtimestamp(dataN/1000).strftime('%Y-%m-%d')
            ref = art.xpath('.//a/@href')[0]
            title = art.xpath('.//a/h2/text()')[0]
            source = art.xpath('.//span[@class ="mg-card-source__source"]/a/text()')[0]
            l.append([source, title, ref, dt])
        return l
