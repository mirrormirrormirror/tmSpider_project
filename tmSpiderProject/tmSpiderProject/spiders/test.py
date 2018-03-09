import pandas
def updateKeyWordToRedis():
    keyWordCsv = pandas.read_excel("../keyWord.xlsx")
    keyWordList = keyWordCsv["关键词"]
    keyWords = keyWordList.values
    for keyWord in keyWords:
       print(keyWord)
if __name__ == '__main__':
    updateKeyWordToRedis()
