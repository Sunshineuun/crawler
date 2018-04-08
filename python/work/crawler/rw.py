#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 人卫助手
import json
import random

import requests
from bs4 import BeautifulSoup, Tag
from requests.exceptions import ChunkedEncodingError

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger, PROXY_IP, PROXY_IP2

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
                        self._urlpool.update({'_id': data['_id']}, {'$set': {'isenable': '0'}})
                        url_r.clear()
                    except BaseException as ex:
                        logger.error(ex)
                        logger.error(data)
            else:
                try:
                    res = requests.get(data['url'], proxies=random.choice(PROXY_IP2))
                except ChunkedEncodingError as chunkedEncodingError:
                    logger.error(chunkedEncodingError)
                    continue
                except ConnectionResetError as connectionResetError:
                    # 远程主机强迫关闭了一个现有的连接。
                    logger.error(connectionResetError)
                    continue

                if res.status_code == 200:
                    data['html'] = res.text
                    self.save_html(h=res.text, p=data)
                else:
                    logger.error(data['url'])

    def parser(self):
        """
        title - 中文名称
        englishDis - 英文名称
        englishDisAlias - 英文别名
        chineseDisAlias - 别名
        disDesc - 概述
        disClinical - 临床表现
        disDiagnose - 诊断
        disTreat - 治疗
        disProg - 预后
        disPreventive - 预防
        icd10Code - icd
        icd9CmCode - icd9
        from - 来源

        :return:
        """
        keys = ['title', 'chineseDisAlias', 'englishDis', 'englishDisAlias', 'icd10Code', 'icd9CmCode', 'from', ]
        for d in self._html_cursor.find({'title': {'$exists': 'true'}}):
            p = {
                '_id': d['_id'],
                'url': d['url']
            }
            for k in keys:
                p[k] = d[k]
            soup = BeautifulSoup(d['html'], 'html.parser')
            divs = soup.find('div', class_='mechanism_top mechanism_bottom')
            for div in divs.children:
                if type(div) != Tag:
                    continue
                if len(div.contents) < 3:
                    continue
                p[div.contents[1].text] = div.contents[3].text
            self._data_cursor.insert_one(p)



