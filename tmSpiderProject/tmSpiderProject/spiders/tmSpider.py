import re
import time
import scrapy
import logging
import redis
from scrapy import Request
from bs4 import BeautifulSoup
from ..items import TmspiderprojectItem
from ..settings import *
import pandas

logger = logging.getLogger("searchSpider")

def updateKeyWordToRedis():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PRORT, db=REDIS_DB)
    keyWordCsv = pandas.read_excel("C:\\Users\\20170912A2\\PycharmProjects\\c2c-spider\\c2c-spiderProject\\tmSpiderProject\\tmSpiderProject\\keyWord.xlsx")
    keyWordList = keyWordCsv["关键词"]
    keyWords = keyWordList.values
    for keyWord in keyWords:
        logging.info("redisKeyWord:" + keyWord)
        r.sadd(NEW_KEYWORD, keyWord)

class tmSpider(scrapy.spiders.Spider):
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PRORT, db=REDIS_DB)

    name = "tmSpider"
    allowed_domains = ["tmall.com"]

    def start_requests(self):
        while True:
            newKeyWordLen = self.r.scard(NEW_KEYWORD)
            if int(newKeyWordLen) > 0:
                pages = []
                keyWord = self.r.spop(NEW_KEYWORD)
                url = 'https://list.tmall.com/search_product.htm?q=' + keyWord.decode()
                meta = {"keyWord": keyWord.decode()}
                logging.info("firstKeyWord:" + keyWord.decode())
                page = scrapy.Request(url, meta=meta)
                page.meta["installProxy"] = True
                pages.append(page)
                return pages
            else:
                updateKeyWordToRedis()

    def parse(self, response):

        soup = BeautifulSoup(response.text)
        item = TmspiderprojectItem()
        pageIndex = 1
        # 当时第一页的时候才这样子做
        tipTag = soup.select(".searchTip")
        if len(tipTag) > 0:
            return
        if "&s=" not in response.url and "q=" in response.url:
            logger.info("test" + str(response.url))
            totalPage = soup.select("input[name=totalPage]")[0].attrs["value"]
            logging.info("totalPage:" + totalPage)
            if int(totalPage) < 5:
                pageNum = int(totalPage)
            else:
                pageNum = 5
            for page in range(pageNum):
                url = response.url + "&s=" + str(page * 60)
                meta = {"keyWord": response.meta["keyWord"]}
                request = Request(url=url, callback=self.parse, meta=meta)
                request.meta["installProxy"] = True
                yield request
        else:
            logging.info("logurl:" + response.url)
            sNum = re.findall(r's=\d+', response.url)[0].split("=")[1]
            pageIndex = int(sNum) / 60 + 1
        productList = soup.select(".product-iWrap")
        index = 1
        logging.info("productList:" + str(len(productList)))
        for product in productList:
            # 对于专辑可以跳过
            # 这个是每一个商品的循环
            if len(product.select(".pal-resume")) > 0:
                logging.error("get message err")
                break
            # 产品id
            product = BeautifulSoup(str(product))
            productId = re.findall("tmall.com/item.htm\?id=(.*?)&", str(product))
            if len(productId) == 0:
                productId = "0"
            else:
                productId = productId[0]
            # 价格
            price = product.select(".productPrice")[0].select("em")[0].attrs["title"]
            productStatus = product.select(".productStatus")
            # 月销量
            monthSales = productStatus[0].select("span em")[0].get_text()
            # 当前评论数
            logging.info("commentsNum:" + str(productStatus[0]))
            commentsNum = re.findall('J_TabBar" target="_blank">(.*?)</a>', str(product))[0]
            # commentsNum = productStatus[0].select(".productStatus > span:nth-child(2) > a")[0].get_text()
            dataAtp = product.select(".ww-small")[0].attrs["data-atp"]
            # 爬评论的时候有用
            sellerId = dataAtp.split(",")[-1]
            # 当前页的物品排名
            itemIndex = index
            index = index + 1
            keyWord = response.meta["keyWord"]
            item["keyWord"] = keyWord
            item["pageIndex"] = pageIndex
            item["productId"] = productId
            item["price"] = price
            item["commentsNum"] = commentsNum
            item["sellerId"] = sellerId
            item["itemIndex"] = itemIndex
            item["monthSales"] = monthSales
            logging.info(item)
            # detail页获取keyWord
            self.r.sadd(DETAIL_PRODUCE_ID, productId)
            # 评论爬虫从redis中读取meta
            self.r.sadd(COMMENT_PRODUCE_ID, productId)
            self.r.hset(COMMENT_FEED, productId, sellerId)
            yield item
        while True:
            newKeyWordLen = self.r.scard(NEW_KEYWORD)
            if int(newKeyWordLen) > 0:
                keyWord = self.r.spop(NEW_KEYWORD)
                requestUrl = 'https://list.tmall.com/search_product.htm?q=' + keyWord.decode()
                meta = {"keyWord": keyWord.decode()}
                nextRequest = scrapy.Request(requestUrl, meta=meta)
                nextRequest.meta["installProxy"] = True
                logging.info("nextKeyWord:" + keyWord.decode())
                yield nextRequest
                break
            else:
                updateKeyWordToRedis()


