#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import re

import chardet
from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import reg

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

        self.init_url()

    def init_url(self):
        logger.info('url初始开始！')
        url = 'http://zhongyaofangji.com/all.html'
        logger.info('请求开始......')
        html = self.crawler.request_get_url(url)
        # logger.info('获取编码......')
        # from_encoding = chardet.detect(html)

        logger.info('对象转换开始......')
        soup = BeautifulSoup(html, 'html.parser', from_encoding='gb2312')
        print(soup.original_encoding)

        logger.info('获取标签开始......')
        a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z]+.html'))

        logger.info('遍历存储开始......')
        _id = 0
        for a in a_tags:
            params = {
                '_id': _id,
                'url': a['href'],
                'type': 'zhongyaofangji-中药方剂'
            }
            self.urlpool.save_to_db(params)
            _id += 1
        logger.info('url初始结束！')

    def request_data(self):
        encodings = ['Windows-1252', 'gb2312', 'gbk']
        html_crusor = self.mongo.get_cursor(self.name, 'html')
        while not self.urlpool.empty():
            data = self.urlpool.get()
            try:
                d1 = datetime.datetime.now()
                html_str = None
                for encoding in encodings:
                    try:
                        html_str = self.crawler.request_get_url(data['url']).decode(encoding)
                        break
                    except UnicodeDecodeError as error:
                        logger.error(error)

                if not html_str:
                    self.urlpool.update({
                        'url': data['url']
                    }, {
                        '$set': {
                            'isenable': '1'
                        }
                    })
                    continue

                # soup = BeautifulSoup(html_str, 'html.parser', from_encoding='gb2312')
                data['html'] = html_str
                html_crusor.save(data)
                logger.info('耗时.....' + str((datetime.datetime.now() - d1).total_seconds()))
            except BaseException as e:
                logger.error(data['url'])
                logger.error(e)
                pass

    def parser(self):
        html_crusor = self.mongo.get_cursor(self.name, 'html')
        data_crusor = self.mongo.get_cursor(self.name, 'data')

        for data in html_crusor.find():
            soup = BeautifulSoup(data, 'lxml')
            row = {
                '_id': data['_id'],
                'url': data['url'],
            }
            p_tags = soup.find('p')
            if not len(p_tags):
                self.urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })
                continue

            for p in p_tags:
                tag = reg('【[\u4e00-\u9fa5]+】', p.text)
                row[tag] = p.text.replace(tag, '')

            data_crusor.insert(row)

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
    zyfz.request_data()
