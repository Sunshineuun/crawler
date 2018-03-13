#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import re
from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool

logger = mlogger.get_defalut_logger('./log/zhongyoo.log', 'zhongyoo')


class zhongyaofangji(object):
    def __init__(self, ip='127.0.0.1'):
        """
        :param ip: mongodb的ip地址
        """
        self.pici = 0
        self.name = 'zhongyaofangji'

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler(urlpool=self.urlpool)

        # self.init_url()

    def init_url(self):
        url = 'http://zhongyaofangji.com/all.html'
        html = self.crawler.driver_get_url(url)
        soup = BeautifulSoup(html, 'html.parser')
        a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z]+.html'))
        _id = 0
        for a in a_tags:
            params = {
                '_id': _id,
                'url': a['href'],
                'type': 'zhongyaofangji-中药方剂'
            }
            self.urlpool.save_to_db(params)
            _id += 1

    def request_data(self):
        zhongyaofangji_html_crusor = self.mongo.get_cursor(self.name, 'html')
        while not self.urlpool.empty():
            params = self.urlpool.get()
            try:
                html_str = self.crawler.request_get_url(params['url']).decode('gbk')
                params['html'] = html_str
                zhongyaofangji_html_crusor.save(params)
            except BaseException as e:
                logger.error(e)
                pass

    def parser(self):
        pass

    def test(self):
        try:
            url = 'http://zhongyaofangji.com/a/aaiwan.html'
            html = self.crawler.request_get_url(url).decode('gbk')
            soup = BeautifulSoup(html, 'html.parser')
            a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z]+.html'))
            _id = 0
            for a in a_tags:
                params = {
                    '_id': _id,
                    'url': a['href'],
                    'type': 'zhongyaofangji-中药方剂'
                }
                self.urlpool.save_to_db(params)
                _id += 1
        except BaseException:
            pass
        finally:
            self.crawler.get_driver().stop_client()

        print(1)


if __name__ == '__main__':
    # TODO 修改URL存储的地址
    zyfz = zhongyaofangji('192.168.16.113')
    zyfz.test()
