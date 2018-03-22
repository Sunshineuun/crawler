#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
"""
中药方剂大全：http://www.zhongyoo.com/fangji/
"""

from bs4 import BeautifulSoup

from minnie.crawler.common.Utils import reg
from python.no_work.utils import logger
from python.no_work.utils.urlpool import URLPool
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.mongodb import MongodbCursor

logger = logger.get_defalut_logger('./log/zhongyoo.log', 'zhongyoo')


class zhongyoo(object):
    def __init__(self, ip='127.0.0.1'):
        """
        """
        self.name = 'zhongyoo'
        self.pici = 1
        self.url_index = 0  # 插入文档中的ID设置

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler()

        self.init_url()

    def init_url(self):
        """
        起始地址：http://www.zhongyoo.com/fangji/
        :return:
        """
        self.url_index = self.urlpool.find_all_count()
        if self.url_index:
            return

        params = {
            'type': 'zhongyoo-中药方剂'
        }
        for i in range(1, 5):
            self.url_index = i
            params['_id'] = i
            params['url'] = 'http://www.zhongyoo.com/fangji/page_{index}.html'.format(index=i)
            self.urlpool.save_url(params)

    def request_date(self):
        """
        请求数据
        :return:
        """
        encodings = ['gb2312', 'gbk', 'Windows-1252']
        html_crusor = self.mongo.get_cursor(self.name, 'html')
        while not self.urlpool.empty():
            data = self.urlpool.get()
            html_str = None
            try:
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

                data['html'] = html_str
                html_crusor.save(data)
                self.urlpool.update_success_url(data['url'])
            except BaseException as e:
                logger.error(data['url'] + '出现以下错误>>>>>>>>>>>>')
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
                row = {
                    'url': data['url']
                }
                tag = ''
                for p in p_tags:
                    if reg('【[\u4e00-\u9fa5]+】', p.text):
                        tag = reg('【[\u4e00-\u9fa5]+】', p.text)
                        row[tag] = str(p.text).replace(tag, '')
                    elif reg('[\u4e00-\u9fa5]+', tag):
                        row[tag] += p.text

                if '【方剂名】' in row \
                        and str(row['【方剂名】']).__contains__('，'):
                    index = row['【方剂名】'].index('，')
                    temp = row['【方剂名】']
                    row['【方剂名】'] = temp[0:index]
                    row['【方剂出处】'] = temp[index + 1:]
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

    # zyfz.request_date()
    zyfz.parser()
