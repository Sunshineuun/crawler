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

logger = mlogger.get_defalut_logger('./log/zhongyoo.log', 'zhongyoo')


class zhongyoo(object):
    def __init__(self, _urlpool, _mongo):
        """
        """
        self.urlpool = _urlpool
        self.mongo = _mongo
        self.crawler = Crawler(urlpool=_urlpool, mongo=_mongo)
        self.url_index = 0  # 插入文档中的ID设置

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

        zhongyoo_html_crusor = self.mongo.get_cursor('zyfj', 'zhongyoo_html')
        while not self.urlpool.empty():
            params = self.urlpool.get()
            try:
                html_str = self.crawler.request_get_url(params['url']).decode('gbk')
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
                zhongyoo_html_crusor.insert(params)
            except BaseException as e:
                logger.error(params['url'] + '出现以下错误>>>>>>>>>>>>')
                logger.error(e)


if __name__ == '__main__':
    mongo = MongodbCursor('192.168.16.113')
    # TODO 修改URL存储的地址
    urlpool = URLPool(mongo, 'zhongyaoo_zyfj')
    zyfz = zhongyoo(urlpool, mongo)

    zyfz.request_date()
