import re
import redis
import scrapy
import logging
import json
from multiprocessing import Process
from scrapy import Request
from ..settings import *
from ..items import CommentItem
from ..startMeth import *
import time

logger = logging.getLogger("commentSpider")


class tmSpider(scrapy.spiders.Spider):
    name = "commentSpider"
    allowed_domains = ["tmall.com"]

    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PRORT, db=REDIS_DB)

    def start_requests(self):

        while True:
            itemId = self.r.spop(COMMENT_PRODUCE_ID)
            if itemId is not None:
                pages = []
                if itemId is not None:
                    sellerId = self.r.hget(COMMENT_FEED, itemId.decode())
                    url = "https://rate.tmall.com/list_detail_rate.htm?ItemId=" + itemId.decode() + \
                          "&sellerId=" + sellerId.decode() + "&currentPage=1&callback=json"
                    meta = {"itemId": itemId.decode(), "sellerId": sellerId.decode()}
                    page = scrapy.Request(url, meta=meta)
                    pages.append(page)
                    return pages
            else:
                time.sleep(20)

    def parse(self, response):

        while True:
            itemId = self.r.spop(COMMENT_PRODUCE_ID)
            if itemId is not None:
                sellerId = self.r.hget(COMMENT_FEED, itemId.decode())
                url = "https://rate.tmall.com/list_detail_rate.htm?ItemId=" + itemId.decode() + \
                      "&sellerId=" + sellerId.decode() + "&currentPage=1&callback=json"
                meta = {"itemId": itemId.decode(), "sellerId": sellerId.decode()}
                request = scrapy.Request(url, meta=meta)
                yield request
                break
            else:
                time.sleep(20)

        item = CommentItem()
        produceId = response.meta["itemId"]
        sellerId = response.meta["sellerId"]
        text = response.text.replace("json(", "")
        text = text[0:-1]
        textJson = json.loads(text)
        rateList = textJson["rateDetail"]["rateList"]
        for rate in rateList:
            commentTimeStamp = rate["gmtCreateTime"]
            commentId = rate["id"]
            commentContent = rate["rateContent"]
            if rate["appendComment"] != "":
                commentContent = rate["appendComment"]["content"]

            commentUser = rate["displayUserNick"]
            item["itemId"] = produceId
            item["commentTimeStamp"] = commentTimeStamp
            item["commentId"] = commentId
            item["commentContent"] = commentContent
            item["commentUser"] = commentUser
            yield item

        currenPage = re.findall(r'currentPage=\d+', response.url)[0].split("=")[1]
        if int(currenPage) != 1:
            lastPage = textJson["rateDetail"]["paginator"]["lastPage"]
            if lastPage >= 5:
                lastPage = 5

            for page in range(lastPage + 1):
                # 只要2，3,4,5页
                if page > 1:
                    url = "https://rate.tmall.com/list_detail_rate.htm?itemId=" + produceId + \
                          "&sellerId=" + sellerId + "&currentPage=" + str(page + 1) + "&callback=json"
                    logging.info("commentURl:" + url)
                    nextMeta = {"itemId": itemId, "sellerId": sellerId}
                    yield Request(url=url, callback=self.parse, meta=nextMeta)

