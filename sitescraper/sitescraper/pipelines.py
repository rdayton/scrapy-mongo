import pymongo
import datetime

from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            self.collection.insert_one(
                {
                    "account_owner": item["account_owner"],
                    "sites":
                    {
                        item['domain']:
                        {
                            "page" : item["page"],
                            "status" : item["status"],
                            "link_destination" : item["link_destination"],
                            "external_link_status" : item["external_link_status"],
                            "last_scanned": datetime.datetime.now(),
                        }
                    }
                    
                    
                }
            )
            
            log.msg("Site scanned to MongoDB database!",
                    level=log.DEBUG, spider=spider)
        return item
