# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import time
from pymongo import MongoClient
import logging
from tmSpiderProject.items import KeyWordItem, DetailItem, CommentItem, TmspiderprojectItem
from .settings import *
logger = logging.getLogger("piplines")


class tmPipeline(object):
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PRORT, db=REDIS_DB)
        mongoClient = MongoClient(MONGODB_HOST, MONGODB_PRORT)

        self.db = mongoClient[MONGODB_NAME]

    def process_item(self, item, spider):
        mongoData = dict()
        if isinstance(item, KeyWordItem):
            self.r.sadd(NEW_KEYWORD, item["keyWord"])
            collection = self.db[MONGODB_KEYWORD]
            mongoData["rankNum"] = item["rankNum"]
            mongoData["num"] = item["num"]
            mongoData["liftMedian"] = item["liftMedian"]
            mongoData["liftRate"] = item["liftRate"]
            mongoData["keyWord"] = item["keyWord"]
            mongoData["updateTime"] = time.time()
            collection.insert(mongoData)
        if isinstance(item, DetailItem):
            collection = self.db[MONGODB_DETAIL]
            mongoData["trueAddressQuantity"] = item["trueAddressQuantity"]
            mongoData["collectNum"] = item["collectNum"]
            mongoData["destailsDict"] = item["destailsDict"]
            mongoData["totalQuantity"] = item["totalQuantity"]
            mongoData["deliveryAddress"] = item["deliveryAddress"]
            mongoData["scoreDescribe"] = item["scoreDescribe"]
            mongoData["scoreService"] = item["scoreService"]
            mongoData["scoreLogistics"] = item["scoreLogistics"]
            mongoData["shopName"] = item["shopName"]
            mongoData["shopTime"] = item["shopTime"]
            mongoData["shopUrl"] = item["shopUrl"]
            mongoData["title"] = item["title"]
            mongoData["itemId"] = item["itemId"]
            mongoData["updateTime"] =  time.time()
            collection.insert(mongoData)
        if isinstance(item, TmspiderprojectItem):
            collection = self.db[MONGODB_SEARCH]
            mongoData["keyWord"] = item["keyWord"]
            mongoData["pageIndex"] = item["pageIndex"]
            mongoData["price"] = item["price"]
            mongoData["monthSales"] = item["monthSales"]
            mongoData["commentsNum"] = item["commentsNum"]
            mongoData["sellerId"] = item["sellerId"]
            mongoData["itemIndex"] = item["itemIndex"]
            mongoData["productId"] = item["productId"]
            mongoData["updateTime"] =  time.time()
            collection.insert(mongoData)
        if isinstance(item, CommentItem):
            collection = self.db[MONGODB_COMMENT]
            mongoData["itemId"] = item["itemId"]
            mongoData["commentTimeStamp"] = item["commentTimeStamp"]
            mongoData["commentContent"] = item["commentContent"]
            mongoData["commentId"] = item["commentId"]
            mongoData["commentUser"] = item["commentUser"]
            mongoData["updateTime"] =  time.time()
            collection.insert(mongoData)
        return item
