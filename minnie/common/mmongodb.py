#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import pymongo
from bs4 import BeautifulSoup

from minnie.common import moracle


class MinnieMongo:
    def __init__(self):
        self.client = pymongo.MongoClient('192.168.16.113', 27017)
        self.cursor = moracle.OralceCursor()

    def CFDA(self):
        db = self.client['CFDA']
        _info = db['info']

        sql = "SELECT CODE,TYPE,HTML FROM CFDA_DRUG_HTML"
        drug_html_data = self.cursor.fechall(sql=sql)
        for data in drug_html_data:
            doc = BeautifulSoup(data[2], 'html.parser')
            tr_el = doc.find_all('tr')[1:-3]  # -3还是-4还需要进行测试调整下  TODO
            info_params = {}
            for tr in tr_el:
                tds = tr.find_all('td')
                info_params[tds[0].text] = tds[1].text
            _info.insert(info_params)


if __name__ == '__main__':
    # mongo = MinnieMongo()
    # mongo.CFDA()
    db = pymongo.MongoClient('192.168.16.113', 27017)['CFDA']
    info = db['info']
    datas = info.find()
    print(1)
