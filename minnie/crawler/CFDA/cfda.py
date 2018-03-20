#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import datetime
import random
import time
import traceback

import re
from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import reg

logger = mlogger.get_defalut_logger('cfda.log', 'cfda')


class cfda(object):
    """
    国家食品药品监督管理总局
    """

    def __init__(self, ip='127.0.0.1'):
        self.name = 'cfda'
        self.pici = 0
        self.url_index = 0

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler()

        self.html_cursor = self.mongo.get_cursor(self.name, 'html')
        self.time_cursor = self.mongo.get_cursor(self.name, 'time')
        self.data_cursor = self.mongo.get_cursor(self.name, 'data')

        d1 = datetime.datetime.now()
        self.init_url()
        d2 = datetime.datetime.now()
        logger.info('初始化url耗时' + str((d2 - d1).total_seconds()))

    def init_url(self):
        """
        http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}
        code:25代表国产药品，36代表进口药品
        page:翻页参数
        :return:
        """
        self.url_index = self.urlpool.find_all_count()
        if self.url_index:
            return

        # 国产药品
        url_template = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}'
        _params = {
            '国产': {
                'code': 25,
                'page': 11061
            },
            '进口': {
                'code': 36,
                'page': 274
            }
        }
        result_list = []
        for k, v in _params.items():
            for i in range(1, v['page'] + 1):
                _p = {
                    '_id': str(v['code']) + str(i),
                    'url': url_template.format(code=v['code'], page=i),
                    'type': 'CFDA-国产药'
                }
                result_list.append(_p)
        self.urlpool.save_url(result_list)
        self.url_index = self.urlpool.find_all_count()

    def get_cookie(self):
        cookie = ''
        for dic in self.crawler.get_driver().get_cookies():
            cookie += dic['name'] + '=' + dic['value'] + ';'
        return cookie

    def startup(self):
        # 域名前缀
        domain_url = 'http://app1.sfda.gov.cn/datasearch/face3/'
        href_re = 'javascript:commitForECMA[\u4e00-\u9fa50-9a-zA-Z\(\)\?&=,\'.]+'

        while not self.urlpool.empty():
            d1 = datetime.datetime.now()
            params = self.urlpool.get()
            # html_b = self.crawler.request_get_url(params['url'], header={'Cookie': self.get_cookie()})
            # html = html_b.decode('utf-8')
            html = self.crawler.driver_get_url(params['url'])
            soup = BeautifulSoup(html, 'html.parser')
            if params['url'].__contains__('search.jsp'):
                a_tags = soup.find_all('a', href=re.compile(href_re))

                # if not a_tags or len(a_tags) == 0:
                #     html = self.crawler.driver_get_url(params['url'])

                # soup = BeautifulSoup(html)
                # a_tags = soup.find_all('a', href=re.compile(href_re))

                if a_tags and len(a_tags):
                    params['html'] = html
                    self.html_cursor.insert(params)
                    self.urlpool.update_success_url(params['url'])
                    params.pop('html')

                    url_list = []
                    # 更新链接请求成功
                    for a in a_tags:
                        _p = {
                            '_id': self.url_index,
                            'type': params['type'],
                            'url': domain_url + reg(
                                'content.jsp\?tableId=[0-9]+&tableName=TABLE[0-9]+&tableView=[\u4e00-\u9fa50]+&Id=[0-9]+',
                                a['href']),
                            'text': a.text
                        }
                        self.url_index += 1
                        url_list.append(_p)
                    self.urlpool.save_url(url_list)
            elif params['url'].__contains__('content.jsp'):
                tbody = soup.find_all('tbody')
                # if tbody:
                #     html = self.crawler.driver_get_url(params['url'])
                #
                # soup = BeautifulSoup(html)
                # tbody = soup.find_all('tbody')
                if tbody:
                    params['html'] = html
                    # 保存html数据
                    self.html_cursor.insert(params)
                    # 更新数据
                    self.urlpool.update_success_url(params['url'])
            else:
                logger.error('异常情况：' + params['url'])

            d2 = datetime.datetime.now()
            logger.info('耗时：' + str((d2-d1).total_seconds()))

    def parser(self):
        query = {'url': {'$regex': 'http:[a-z0-9/.]+content.jsp\?'}}
        for i, data in enumerate(self.html_cursor.find(query)):
            if i % 1000 == 0:
                logger.info(i)
            soup = BeautifulSoup(data['html'], 'html.parser')
            tr_tags = soup.find_all('tr')[1:-3]
            for tr in tr_tags:
                td = tr.td
                # TODO 格式化数据

    def save_oracle(self):
        sql = ''


if __name__ == '__main__':
    z = cfda('192.168.16.113')
    z.parser()
