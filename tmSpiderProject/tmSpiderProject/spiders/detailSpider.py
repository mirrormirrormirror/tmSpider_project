import redis
import scrapy
import logging
import re
import json
from bs4 import BeautifulSoup
from retry import retry
from ..items import DetailItem
import requests
import urllib.request as ur
from ..settings import *
import time

logger = logging.getLogger("detailSpider")


@retry(delay=2)
def getHtml(url, referen='', protocol='http', openProxies=True):
    if not url.startswith(protocol):
        url = protocol + '://' + url
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',
        'Referer': referen,
    }
    if openProxies:
        # 获取代理ip
        ip = ur.urlopen(
            'http://api.ip.data5u.com/dynamic/get.html?order=0d171ac67a30b8ef3791b18d806f7c7f&sep=4').read()[
             :-1]
        proxies = {'https': 'https://' + ip.decode()}
        page = requests.get(url, headers=headers, timeout=5, proxies=proxies, cookies={})
    else:
        page = requests.get(url, headers=headers, timeout=5, cookies={})
    if page.status_code != 200 or "window.location.href" in page.text:
        raise ("get page fail")
    return page.text


class detailSpider(scrapy.spiders.Spider):
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PRORT, db=REDIS_DB)

    name = "detailSpider"
    allowed_domains = ["tmall.com"]

    def start_requests(self):
        while True:
            detailProductIdLen = self.r.scard(DETAIL_PRODUCE_ID)
            if int(detailProductIdLen) > 0:
                detailProductId = self.r.spop(DETAIL_PRODUCE_ID)
                pages = []
                url = "https://detail.tmall.com/item.htm?id=" + detailProductId.decode()
                meta = {"detailProductId": detailProductId.decode()}
                page = scrapy.Request(url, meta=meta)
                pages.append(page)
                return pages
            else:
                time.sleep(20)

    def parse(self, response):
        # 爬取下一个
        while True:
            detailProductIdLen = self.r.scard(DETAIL_PRODUCE_ID)
            if int(detailProductIdLen) > 0:
                detailProductId = self.r.spop(DETAIL_PRODUCE_ID)
                if detailProductId is not None:
                    url = "https://detail.tmall.com/item.htm?id=" + detailProductId.decode()
                    meta = {"detailProductId": detailProductId.decode()}
                    request = scrapy.Request(url, meta=meta)
                    yield request
                break
            else:
                time.sleep(20)
        item = DetailItem()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.select("title")[0].get_text()
        destailsDict = []
        detailList = soup.select("#J_AttrUL li")
        div = soup.select('div[id="shop-info"]')
        scores = [x.get_text() for x in div[0].select('span[class="shopdsr-score-con"]')[:3]]
        scoreDescribe = "0"
        scoreService = "0"
        scoreLogistics = "0"
        if len(scores) == 3:
            scoreDescribe = scores[0]
            scoreService = scores[1]
            scoreLogistics = scores[2]
        shopTime = ""
        shopTimeTag = div[0].select('span[class="tm-shop-age-content"]')
        if len(shopTimeTag) != 0:
            shopTime = shopTimeTag[0].get_text()
        shopUrlTag = soup.select(".slogo-shopname")
        shopName = ""
        shopUrl = ""
        if len(shopUrlTag) > 0:
            shopName = soup.select('.slogo-shopname strong')[0].get_text()
            shopUrl = shopUrlTag[0].attrs["href"]

        item["scoreDescribe"] = scoreDescribe
        item["scoreService"] = scoreService
        item["scoreLogistics"] = scoreLogistics
        item["shopName"] = shopName
        item["shopTime"] = shopTime
        item["shopUrl"] = shopUrl
        for detail in detailList:
            detail = BeautifulSoup(str(detail))
            detailText = detail.select("li")[0].get_text()
            # 英文分号
            keyAndValue = detailText.split(":")
            if len(keyAndValue) == 1:
                # 中文分号
                keyAndValue = detailText.split("：")
            detailTmp = {}
            key = keyAndValue[0]
            value = keyAndValue[1]
            detailTmp[key] = value
            destailsDict.append(detailTmp)
        pageStr = getHtml(
            'https://count.taobao.com/counter3?_ksTS=1501297231590_239&callback=jsonp25&keys=ICCP_1_' + response.meta[
                "detailProductId"], openProxies=False)
        pageJsonStr = re.findall(r'\((.*?)\);', pageStr)[0]
        # logger.info("pageJson:" + pageJsonStr)
        collectNum = json.loads(pageJsonStr)['ICCP_1_' + response.meta["detailProductId"]]
        item["destailsDict"] = destailsDict
        item["collectNum"] = collectNum
        url = "http://mdskip.taobao.com/core/initItemDetail.htm?tmallBuySupport=true&itemId=%s&service3C=true" % \
              response.meta["detailProductId"]
        data = getHtml(url,
                       referen="http://detail.tmall.com/item.htm?id=%s" % response.meta["detailProductId"])
        '''库存'''
        trueAddressQuantity = 1
        try:
            page_json = json.loads(data)
            totalQuantity = 0
            deliveryAddress = ""
            if page_json['defaultModel']['inventoryDO']['totalQuantity'] is not None:
                totalQuantity = page_json['defaultModel']['inventoryDO']['totalQuantity']
            if page_json['defaultModel']['deliveryDO']['deliveryAddress'] is not None:
                deliveryAddress = page_json['defaultModel']['deliveryDO']['deliveryAddress']
        except:
            # 从redis中拿一个随机的出来
            randCity = self.r.srandmember("city")
            deliveryAddress = randCity.decode()
            rand1 = self.r.srandmember("randTotalQuantity")
            rand2 = self.r.srandmember("randTotalQuantity")
            trueAddressQuantity = 0
            import random
            # 在两个随机的中间抽一个出来
            if int(rand1.decode()) > int(rand2.decode()):
                totalQuantity = random.randint(int(rand2.decode(), int(rand1.decode())))
            else:
                totalQuantity = random.randint(int(rand1.decode(), int(rand2.decode())))

        item["deliveryAddress"] = deliveryAddress
        item["trueAddressQuantity"] = trueAddressQuantity
        item["totalQuantity"] = totalQuantity
        item["title"] = title
        item["itemId"] = response.meta["detailProductId"]
        yield item
