import requests
from pprint import pprint
import json

# Задаем имя
NAME = 'papalos'

# Получаем ответ от API и преобразуем в json
j = requests.get(f'https://api.github.com/users/{NAME}/repos').json()

# При необходимости просматриваем ответ
# pprint(j)

# Сохраняем ответ в файл
with open("rep.json", "w") as f:
    json.dump(j, f)

# Выводим ответ список репозиториев (по заданию)
print(NAME.upper(), ": ")
print(*[i['name'] for i in j], sep='\n')