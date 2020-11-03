from scrapy.pipelines.images import ImagesPipeline
import scrapy


# --------- sqlalchemy --------------
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from modelLerua import Base, Lerua


class DataBasePipeline:
    def __init__(self):
        engine = create_engine('sqlite:///leruaDB.db', echo=True)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    def process_item(self, item, spider):
        new_vacancy = Lerua(
            title=item['title'],
            link=item['link'],
            price=item['price'],
            photos=r'/photo/' + item['title'],
            feature=str(item['feature'])
        )
        try:
            self.session.add(new_vacancy)
            self.session.commit()
        except IntegrityError:
            print('Проблема с загрузкой Данных!')
            self.session.rollback()
        return item

    def __del__(self):
        self.session.close()


class LeruaPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        print('-------------->', item)
        if item['photo_links']:
            for img_link in item['photo_links']:
                try:
                    yield scrapy.Request(img_link, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None):
        item = request.meta
        name = request.url.split('/')[-1]
        return f"/{item['title']}/{name}"

    def item_completed(self, results, item, info):
        if results:
            item['photo_links'] = [itm[1] for itm in results if itm[0]]
        return item

