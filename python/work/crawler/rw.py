#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 人卫助手
import json

import requests
import time
from bs4 import BeautifulSoup, Tag
from bson import InvalidDocument

from python.no_work.crawler.base_crawler import BaseCrawler


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

    def startup(self, d):
        header = {
            'Content-Type': 'application/json',
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

        time.sleep(2)

        if 'pageNo' in d:
            print(d['pageNo'])
            params['pageNo'] = d['pageNo']
            res = requests.post(url=d['url'], data=json.dumps(params), headers=header)
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
                    self.save_html(h=res.text, p1=d)
                    url_r.clear()
                except BaseException as ex:
                    self.log.error(ex)
                    self.log.error(d)
        else:
            res = self._crawler.get(d['url'])
            if res.status_code == 200:
                self.save_html(h=res.text, p1=d)
            else:
                self.log.error(d['url'])

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
        self.get_data_cursor().delete_many({})

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
            if divs is None:
                state = str(self._urlpool.update({'_id': d['_id']}, {'$set': {'isenable': '1'}}))
                print(self._html_cursor.delete_one({'_id': d['_id']}))
                print('错误数据更新：{url}，状态{state}'.format(url=d['url'], state=state))
                continue
            try:
                for div in divs.children:
                    if type(div) != Tag:
                        continue
                    if len(div.contents) < 4:
                        continue
                    p[div.contents[1].text.replace('.', '')] = div.contents[3].text
                self._data_cursor.insert_one(p)
            except AttributeError as attributeError:
                self.log.error(attributeError)
                self.log.error(d['url'])
            except InvalidDocument as e:
                # key '1.诊断' must not contain '.' BSONError;MongoDB插入异常
                self.log.error(e)
