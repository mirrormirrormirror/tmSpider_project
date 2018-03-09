# -*- coding: utf-8 -*-

# redis数据配置
COMMENT_PRODUCE_ID = "commentProductId"
DETAIL_PRODUCE_ID = "detailProductId"
COMMENT_FEED = "commentFeed"
REDIS_HOST = '191k34m630.51mypc.cn'
REDIS_PRORT = 18650
REDIS_DB = 1
NEW_KEYWORD = "newKeyWord"
OLD_KEYWORD = "oldKeyWord"
# mongodb信息配置
MONGODB_HOST = "191k34m630.51mypc.cn"
MONGODB_PRORT = 35519
MONGODB_NAME = "tmdb"
MONGODB_KEYWORD = "keyWord"
MONGODB_DETAIL = "detail"
MONGODB_SEARCH = "search"
MONGODB_COMMENT = "comment"

# 其他信息配置
BOT_NAME = 'tmSpider'
SPIDER_MODULES = ['tmSpiderProject.spiders']
NEWSPIDER_MODULE = 'tmSpiderProject.spiders'
DOWNLOADER_MIDDLEWARES = {
    'tmSpiderProject.middlewares.PhantomJSMiddleware': 100
}


ROBOTSTXT_OBEY = False
COOKIES_ENABLED = False

ITEM_PIPELINES = {
  'tmSpiderProject.pipelines.tmPipeline': 3,
}

#超时设置
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 408, 302, 303]
