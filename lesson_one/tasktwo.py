import requests
from pprint import pprint
import json

TOKEN = ''
p = {
    'user_id': 486973140,
    'fields': 'true',
    'v': '5.52',
    'access_token': 'тут должен быть токен'
    }
j = requests.get('https://api.vk.com/method/friends.get', params=p).json()

#pprint(j)

#print(*[f"{i['last_name']} {i['first_name']}" for i in j['response']['items']], sep='\n')

ll = []
for i in j['response']['items']:
    dd = {}
    for j, k in i.items():
        if j == 'first_name' or j == 'last_name':
            dd[j] = k
    ll.append(dd)

pprint(ll)
#jj = json.dumps(ll, ensure_ascii=True)
# Сохраняем ответ в файл
with open("userfr.json", "w", encoding='utf-8') as f:
    json.dump(ll, f, ensure_ascii=False, indent=4)
