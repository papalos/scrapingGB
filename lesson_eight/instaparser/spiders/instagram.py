import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser import config #должен быть создан вручную и содержит приватные переменные


class InstagramSpider(scrapy.Spider):

    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['http://instagram.com/']

    insta_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = 'https://www.instagram.com/graphql/query/'
    followers_hash = 'c76146de99bb02f6415203be841dd25a'
    followings_hash = 'd04b0a864b4b54837c0d870b0e77e076'

    insta_login = 'здесь логин'
    insta_psw = 'Здесь зашифрованный пароль'
    target_accounts = ['ai_machine_learning', 'omgames_blog']  # список (list) целевых аккаунтов, которые будем парсить

    def parse(self, response: HtmlResponse):
            csrf_token = self.fetch_csrf_token(response.text)  # получаем csrf
            yield scrapy.FormRequest(                         #авторизуемся
                url=self.insta_login_link,
                method='POST',
                callback=self.login,
                formdata={'username': self.insta_login, 'enc_password': self.insta_psw},
                headers={'X-CSRFToken': csrf_token}
            )

    def login(self, response: HtmlResponse):
        j_body = json.loads(response.text)
        if j_body['authenticated']:
            for account in self.target_accounts:    #переходим на каждую страницу целевых аккаунтов для парсинга
                yield response.follow(
                    f'/{account}',
                    callback=self.target_user_parse,
                    cb_kwargs={'target_username': account}
                )

    def target_user_parse(self, response: HtmlResponse, target_username):
        target_user_id = self.fetch_user_id(response.text, target_username)
        variables = {'id': target_user_id,
                     'first': 24
                     }

        #! парсим подписанных на целевой аккаунт
        # По адресу graphql запрашиваем данные с хешем фоловеров
        url_followers = f'{self.graphql_url}?query_hash={self.followers_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followers,
            callback=self.users_parse,
            cb_kwargs={'target_username': target_username, 'flag': 'followers',  'variables': deepcopy(variables)}
        )

        # ! парсим на кого подписан целевой аккаунт
        # По адресу graphql запрашиваем данные с хешем отслеживаемых акаунтов
        url_followings = f'{self.graphql_url}?query_hash={self.followings_hash}&{urlencode(variables)}'
        yield response.follow(
            url_followings,
            callback=self.users_parse,
            cb_kwargs={'target_username': target_username, 'flag': 'followings', 'variables': deepcopy(variables)}
        )

    def users_parse(self, response: HtmlResponse, target_username, flag, variables):
        # Получаем текст ответа
        j_data = json.loads(response.text)
        # в зависимости от вызвавшего метода присваеиваем значение параметру type_field
        type_field = 'edge_followed_by' if flag == 'followers' else 'edge_follow'
        # из ответа забираем page_info
        page_info = j_data.get('data').get('user').get(type_field).get('page_info')
        # если page_info имеет информацию о следующей странице, забираем указатель на нее и уходим в рекурсию
        if page_info['has_next_page']:
            variables['after'] = page_info['end_cursor']

            url = f"{response.url[:response.url.find('&')]}&{urlencode(variables)}"
            yield response.follow(
                url,
                callback=self.users_parse,
                cb_kwargs={'target_username': target_username, 'flag': flag, 'variables': deepcopy(variables)}
            )
            # внутри рекурсивного вызова обрабатываем полученный ответ, получая список ребер графа
            users = j_data.get('data').get('user').get(type_field).get('edges')
            for user in users:
                node = user.get('node')
                item = InstaparserItem(
                    _id=node.get('id'),
                    user_name=node.get('username'),
                    full_name=node.get('full_name'),
                    photo=node.get('profile_pic_url'),
                    insert_to_collection=f'{target_username}_{flag}'
                )
                yield item

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')