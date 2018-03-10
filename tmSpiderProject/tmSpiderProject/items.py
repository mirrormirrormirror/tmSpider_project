# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TmspiderprojectItem(scrapy.Item):
    # define the fields for your item here like
    keyWord = scrapy.Field()
    pageIndex = scrapy.Field()
    price = scrapy.Field()
    monthSales = scrapy.Field()
    commentsNum = scrapy.Field()
    sellerId = scrapy.Field()
    itemIndex = scrapy.Field()
    productId = scrapy.Field()
    updateTime = scrapy.Field()

    # pass


class KeyWordItem(scrapy.Item):
    # define the fields for your item here like:
    rankNum = scrapy.Field()
    keyWord = scrapy.Field()
    num = scrapy.Field()
    liftMedian = scrapy.Field()
    liftRate = scrapy.Field()
    updateTime = scrapy.Field()


class DetailItem(scrapy.Item):
    # define the fields for your item here like:
    trueAddressQuantity = scrapy.Field()
    itemId = scrapy.Field()
    title = scrapy.Field()
    collectNum = scrapy.Field()
    destailsDict = scrapy.Field()
    totalQuantity = scrapy.Field()
    deliveryAddress = scrapy.Field()
    scoreDescribe = scrapy.Field()
    scoreService = scrapy.Field()
    scoreLogistics = scrapy.Field()
    shopName = scrapy.Field()
    shopTime = scrapy.Field()
    shopCity = scrapy.Field()
    shopUrl = scrapy.Field()
    updateTime = scrapy.Field()


class CommentItem(scrapy.Item):
    itemId = scrapy.Field()
    commentId = scrapy.Field()
    commentContent = scrapy.Field()
    commentUser = scrapy.Field()
    commentTimeStamp = scrapy.Field()
    updateTime = scrapy.Field()
