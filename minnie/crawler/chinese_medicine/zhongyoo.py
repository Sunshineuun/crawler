#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
"""
中药方剂大全：http://www.zhongyoo.com/fangji/
"""
from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import reg

logger = mlogger.get_defalut_logger('./log/zhongyoo.log', 'zhongyoo')


class zhongyoo(object):
    def __init__(self, ip='127.0.0.1'):
        """
        """
        self.name = 'zhongyoo'
        self.pici = 1
        self.url_index = 0  # 插入文档中的ID设置

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler(urlpool=self.urlpool)

        self.init_url()

    def init_url(self):
        """
        起始地址：http://www.zhongyoo.com/fangji/
        :return:
        """
        self.url_index = self.urlpool.find_all_count()
        if self.url_index:
            return

        self.url_index += 1
        params = {
            '_id': self.url_index,
            'url': 'http://www.zhongyoo.com/fangji/',
            'type': 'zhongyoo-中药方剂'
        }
        self.urlpool.save_to_db(params)

        for i in range(2, 5):
            self.url_index = i
            params['_id'] = i
            params['url'] = 'http://www.zhongyoo.com/fangji/page_{index}.html'.format(index=i)
            self.urlpool.save_to_db(params)

    def request_date(self):
        """
        请求数据
        :return:
        """

        html_crusor = self.mongo.get_cursor(self.name, 'html')
        while not self.urlpool.empty():
            params = self.urlpool.get()
            try:
                html_str = self.crawler.driver_get_url(params['url'])
                soup = BeautifulSoup(html_str, 'html.parser')
                div_lisbox = soup.find('div', class_='listbox')
                if div_lisbox:
                    a_tags = div_lisbox.find_all('a')

                    for a in a_tags:
                        self.url_index += 1
                        new_params = {
                            '_id': self.url_index,
                            'url': 'http://www.zhongyoo.com' + a['href'],
                            'type': '药智网-中药方剂',
                            'name': a.text
                        }
                        self.urlpool.put(new_params)

                params['html'] = html_str
                html_crusor.update(params, {'$set': {'url': params['url']}}, True)
            except BaseException as e:
                logger.error(params['url'] + '出现以下错误>>>>>>>>>>>>')
                logger.error(e)

    def parser(self):
        html_cursor = self.mongo.get_cursor(self.name, 'html')
        data_cursor = self.mongo.get_cursor(self.name, 'data')

        for i, data in enumerate(html_cursor.find()):
            if i % 1000 == 0:
                logger.info(i)
            soup = BeautifulSoup(data['html'], 'html.parser')
            div = soup.find('div', id='contentText')
            if div:
                p_tags = div.find_all('p')
                row = {}
                tag = ''
                for p in p_tags:
                    if reg('【[\u4e00-\u9fa5]+】', p.text):
                        tag = reg('【[\u4e00-\u9fa5]+】', p.text)
                        row[tag] = str(p.text).replace(tag, '')
                    elif reg('[\u4e00-\u9fa5]+', tag):
                        row[tag] += p.text

                row['url'] = data['url']
                data_cursor.save(row)
            else:
                html_cursor.delete_one({'_id': data['_id']})
                logger.error(data['url'])
                self.urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })


if __name__ == '__main__':
    zyfz = zhongyoo('192.168.16.113')

    zyfz.request_date()
    zyfz.parser()
