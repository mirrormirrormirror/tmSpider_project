from scrapy import cmdline
def startKeyWordSpider():
    cmdline.execute('scrapy crawl keyWordSpider'.split())


def startTmSpider():
    cmdline.execute('scrapy crawl tmSpider'.split())


def startDetailSpider():
    cmdline.execute('scrapy crawl detailSpider'.split())


def startCommentSpider():
    cmdline.execute('scrapy crawl commentSpider'.split())