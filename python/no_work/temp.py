#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import json

import requests

from python.no_work.crawler.realty import LianJia
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.excel import WriteXLSX

if __name__ == '__main__':
    # lianjia = LianJia('192.168.16.113')
    # lianjia.parser()
    # w = WriteXLSX(path='D://Temp//链家房产.xlsx')
    # w.write('LianJia', 'data')
    # url = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseList'
    # params = {
    #     'pageNo': '1',
    #     'pageSize': '100',
    #     'searchText': '',
    #     'icd10Code': '',
    #     'departmentCode': '',
    #     'symptomsWords': ''
    # }
    # header = {
    #     'Content-Type':'application/json',
    #     'Cookie': 'jeesite.session.id=1ab0769d482c4068bac4d2a6b3ecec74; JSESSIONID=206209EF59D3A574B729D798F1A607B5'
    # }
    # res = requests.post(url, data=json.dumps(params), headers=header)
    # res_dic = json.loads(res.text)
    user = {
        'username': 'qiushengming@aliyun.com',
        'pwd': 'qd7qrjm3',
        'backurl': 'https://www.yaozh.com/'
    }
    session = requests.session()
    url = 'https://www.yaozh.com/login/'
    res = session.post(url, data=json.dumps(user))

    url = 'https://db.yaozh.com/zhongyaocai/1.html'
    res = session.get(url)

    print(1)
