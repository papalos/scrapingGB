from pymongo import MongoClient

# список, на кого подписан пользователь
def get_followers(name:str):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    profiles = db[name + '_followers']
    for profile in profiles:
        print(profile)

# список подписчиков указанного пользователя
def get_followings(name:str):
    client = MongoClient('localhost', 27017)
    db = client.instagram
    profiles = db[name + '_followings']
    for profile in profiles:
        print(profile)

