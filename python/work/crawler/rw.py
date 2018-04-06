#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 人卫助手
import json

import requests
from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger

logger = mlogger.get_defalut_logger('yaozhi.log', 'yaozhi')


class disease(BaseCrawler):
    """
    疾病
    """
    def _init_url(self):
        params = {
            'pageNo': 1,
            'pageSize': 100,
            'searchText': '',
            'icd10Code': '',
            'departmentCode': '',
            'symptomsWords': ''
        }
        header = {
            'Content-Type': 'application/json',
            'Cookie': 'jeesite.session.id=1ab0769d482c4068bac4d2a6b3ecec74; JSESSIONID=206209EF59D3A574B729D798F1A607B5'
        }
        url = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseList'
        url1 = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseDetail?diseaseId={diseaseId}'
        result = []
        for page in range(98):
            params['pageNo'] += 1
            res = requests.post(url=url, data=json.dumps(params), headers=header)
            if res.status_code == requests.codes.ok:
                res_dic = res.json()
                self._html_cursor.insert_one(res_dic)
                for d in res_dic['list']:
                    self._data_cursor.insert(d)
                    result.append({
                        'url': url1.format(diseaseId=d['diseaseId']),
                        'type': self._get_cn_name()
                    })
            else:
                logger.error(page)
        self._urlpool.save_url(result)

    def _get_name(self):
        return 'rw_disease'

    def _get_cn_name(self):
        return '人卫助手-疾病'

    def startup(self):
        while not self._urlpool.empty():
            data = self._urlpool.get()
            res = requests.get(data['url'])
            if res.status_code == 200:
                data['html'] = res.text
                self._html_cursor.insert(data)
            else:
                logger.error(data['url'])

    def parser(self):
        pass