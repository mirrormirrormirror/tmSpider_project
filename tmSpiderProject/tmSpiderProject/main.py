import time
from multiprocessing import Process
from startMeth import *


if __name__ == '__main__':
    tmSpider = Process(target=startTmSpider)
    tmSpider.start()

    time.sleep(4)
    detailSpider = Process(target=startDetailSpider)
    detailSpider.start()

    time.sleep(4)
    commentSpider = Process(target=startCommentSpider)
    commentSpider.start()
