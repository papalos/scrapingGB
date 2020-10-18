from scrapy import Scraper
# перед запуском скрипта необходимо выполнить modelDB для создания БД

scr = Scraper('тракторист')

print('Парсим Суперджоб')
sj = scr.superjob_parse(scr.get_superjob_text())
print('Добавляем новые вакансии в БД')
# данный метод служит так же и для первоначального заполнения БД (т.к. при этом добаляются тоже новые вакансии)
scr.add_new_vacancy(sj)

print('Парсим ХедХантер')
hh = scr.hh_parse(scr.get_hh_text())
print('Добавляем новые вакансии в БД')
scr.add_new_vacancy(hh)

print('Ищем вакансии подходящие по зарплате')
v = scr.salary_greater_than(100000)
for i in v:
    print(i[0] + ': ' + i[1])
