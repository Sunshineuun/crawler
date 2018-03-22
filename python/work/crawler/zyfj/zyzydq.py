#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import re
import traceback

from bs4 import BeautifulSoup

from minnie.crawler.common.Utils import reg
from python.no_work.utils import logger
from python.no_work.utils.urlpool import URLPool
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.mongodb import MongodbCursor

logger = logger.get_defalut_logger('zyzydq.log', 'zyzydq')


def _replace(s):
    return str(s).replace(u'\u3000', '') \
        .replace('\r', '') \
        .replace('\n', '') \
        .replace('\t', '')


exclude = ['方剂', '用法', '用量', '功能', '主治', '制备方法', '制法', '组成', '处方', '临床', '应用', '事项', '注意',
           '检查', '生化', '预防', '别名', '备注', '适用', '人群', '禁忌', '适应症', '方解', '优点', '治疗', '功效',
           '不良', '反应', '方名', '作用', '主要', '成份']


def isenable(key):
    for ex in exclude:
        if str(key).__contains__(ex):
            return True
    return False


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
            self.urlpool.save_url(params)
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
            div = soup.find('div', class_='art_body')

            row = {
                'name': soup.find(id='art_txt0').text,
                'url': data['url']
            }
            key = None
            a = ['【[\u4e00-\u9fa5]+】', '[\u4e00-\u9fa5]{0,10}：']
            try:
                if div:
                    p_tags = div.find_all('p')
                    for p in p_tags:
                        text = _replace(p.text)

                        for i in a:
                            _key = reg(i, text)
                            if _key and isenable(_key):
                                _key = _key.replace('【', '').replace('】', '').replace('：', '')
                                row[_key] = text.replace(_key, '')
                                key = _key
                                break

                        if key:
                            row[key] += text

                data_cursor.save(row)
            except BaseException as e:
                print(traceback.format_exc())
                print(1)

    def count(self):
        html_cursor = self.mongo.get_cursor(self.name, 'html')
        url_cursor = self.mongo.get_cursor(self.name, 'url')

        print('html:', html_cursor.find().count())
        print('url:', url_cursor.find().count())


if __name__ == '__main__':
    zyfz = zyzydq('192.168.16.113')
    # zyfz.count()
    zyfz.parser()
