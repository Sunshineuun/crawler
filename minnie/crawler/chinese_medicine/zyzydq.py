#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import re
from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import reg

logger = mlogger.get_defalut_logger('zyzydq.log', 'zyzydq')


class zyzydq(object):
    def __init__(self, ip='127.0.0.1'):
        self.name = 'zyzydq'
        self.pici = 0
        self.url_index = 195  # 插入文档中的ID设置

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler()

        self.init_url()

    def init_url(self):
        """
        http://www.zyzydq.com/fangji/daquan/list_140_{}.html
        初始化到数据库中
        :return: 模板
        """
        if self.urlpool.find_all_count():
            return
        url_template = 'http://www.zyzydq.com/fangji/daquan/list_140_{code}.html'
        for i in range(1, 196):
            params = {
                '_id': i,
                'url': url_template.format(code=i),
                'type': '药智网-中药方剂'
            }
            self.urlpool.save_to_db(params)
        logger.info('url初始结束！！！')

    def request_data(self):
        self.pici += 1

        html_cursor = self.mongo.get_cursor(self.name, 'html')

        # 第一阶段
        while not self.urlpool.empty():
            params = self.urlpool.get()

            if not reg('list_140_[0-9]+.html', params['url']):
                self.urlpool.put(params)
                break

            html = self.crawler.request_get_url(params['url']).decode('utf-8')

            soup = BeautifulSoup(html, 'html.parser')

            a_tags = soup.find_all('a', href=re.compile('/fangji/daquan/[0-9]+.html'))
            for a in a_tags:
                self.url_index += 1
                new_params = {
                    '_id': self.url_index,
                    'url': 'http://www.zyzydq.com' + a['href'],
                    'type': '中医中药网-中药方剂'
                }
                self.urlpool.put(new_params)
            self.urlpool.update_success_url(params['url'])

        # 第二阶段
        while not self.urlpool.empty():
            params = self.urlpool.get()

            html = self.crawler.request_get_url(params['url']).decode('utf-8')
            params['html'] = html

            html_cursor.save(params)
            self.urlpool.update_success_url(params['url'])

    def parser(self):
        html_cursor = self.mongo.get_cursor(self.name, 'html')
        data_cursor = self.mongo.get_cursor(self.name, 'data')

        for i, data in enumerate(html_cursor.find()):
            if i % 1000 == 0:
                logger.info(i)
            soup = BeautifulSoup(data['html'], 'html.parser')

    def count(self):
        html_cursor = self.mongo.get_cursor(self.name, 'html')
        url_cursor = self.mongo.get_cursor(self.name, 'url')

        print('html:', html_cursor.find().count())
        print('url:', url_cursor.find().count())


if __name__ == '__main__':
    zyfz = zyzydq('192.168.16.113')
    zyfz.count()
    # zyfz.parser()
