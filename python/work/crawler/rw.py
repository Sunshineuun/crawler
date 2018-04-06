#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 人卫助手
import json
import random

import requests
from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger, PROXY_IP

logger = mlogger.get_defalut_logger('rw.log', 'rw')


class disease(BaseCrawler):
    """
    疾病
    """

    def _init_url(self):

        if self._urlpool.find_all_count():
            return

        url = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseList'
        result = []
        for page in range(1, 98):
            result.append({
                'url': url,
                'type': self._get_cn_name(),
                'pageNo': page
            })
        self._urlpool.save_url(result)

    def _get_name(self):
        return 'rw_disease'

    def _get_cn_name(self):
        return '人卫助手-疾病'

    def startup(self):
        header = {
            'Content-Type': 'application/json',
            # 'Cookie': 'jeesite.session.id=1ab0769d482c4068bac4d2a6b3ecec74; JSESSIONID=206209EF59D3A574B729D798F1A607B5'
        }
        params = {
            'pageNo': 1,
            'pageSize': 100,
            'searchText': '',
            'icd10Code': '',
            'departmentCode': '',
            'symptomsWords': ''
        }
        url1 = 'http://ccdas.ipmph.com/rwDisease/getRwDiseaseDetail?diseaseId={diseaseId}'
        while not self._urlpool.empty():
            data = self._urlpool.get()

            if 'pageNo' in data:
                print(data['pageNo'])
                params['pageNo'] = data['pageNo']
                res = requests.post(url=data['url'], data=json.dumps(params), headers=header)
                if res.status_code == requests.codes.ok:
                    res_dic = res.json()
                    try:
                        url_r = []
                        for d in res_dic['result']['list']:
                            d.update({
                                'url': url1.format(diseaseId=d['diseaseId']),
                                'type': self._get_cn_name()
                            })
                            url_r.append(d)
                        self._urlpool.save_url(url_r)
                        self.save_html(h=res.text, p=data)
                        self._urlpool.update({'_id':data['_id']},{'$set':{'isenable':'0'}})
                        url_r.clear()
                    except BaseException as ex:
                        logger.info(ex)
                        logger.error(data)
            else:
                res = requests.get(data['url'])
                if res.status_code == 200:
                    data['html'] = res.text
                    self.save_html(h=res.text, p=data)
                else:
                    logger.error(data['url'])

    def parser(self):
        pass