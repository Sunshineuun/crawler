#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import re

from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger
from python.no_work.utils.common import reg


class zhongyaofangji(BaseCrawler):
    def __init__(self, ip='127.0.0.1'):
        """
        :param ip: mongodb的ip地址
        """
        super().__init__(ip)
        self.pici = 0

    def _get_cn_name(self):
        return 'zhongyaofangji-中药方剂'

    def _get_name(self):
        return 'zhongyaofangji'

    def _init_url(self):
        if self._urlpool.find_all_count():
            self.log.info('已初始化....重新初始化请清空数据库')
            return
        self.log.info('url初始开始！')
        url = 'http://zhongyaofangji.com/all.html'
        self.log.info('请求开始......')
        html = self._crawler.request_get_url(url)
        # logger.info('获取编码......')
        # from_encoding = chardet.detect(html)

        self.log.info('对象转换开始......')
        soup = BeautifulSoup(html, 'html.parser', from_encoding='gb2312')
        print(soup.original_encoding)

        self.log.info('获取标签开始......')
        a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z0-1_]+.html'))

        self.log.info('遍历存储开始......')
        _id = 0
        for a in a_tags:
            params = {
                '_id': _id,
                'url': a['href'],
                'type': self._cn_name
            }
            self._urlpool.save_url(params)
            _id += 1
            self.log.info('url初始结束！')

    def startup(self, d):
        encodings = ['GB18030', 'Windows-1252', 'gb2312', 'gbk']
        while not self._urlpool.empty():
            data = self._urlpool.get()
            try:
                d1 = datetime.datetime.now()
                html_str = None
                for encoding in encodings:
                    try:
                        html_b = self._crawler.request_get_url(data['url'])
                        html_str = html_b.decode(encoding)
                        break
                    except UnicodeDecodeError as error:
                        self.log.error(error)

                if not html_str:
                    continue

                # soup = BeautifulSoup(html_str, 'html.parser', from_encoding='gb2312')
                data['html'] = html_str
                self._html_cursor.save(data)
                self._urlpool.update_success_url(data['url'])
                self.log.info('耗时.....' + str((datetime.datetime.now() - d1).total_seconds()))
            except BaseException as e:
                self.log.error(data['url'])
                self.log.error(e)
                pass

    def parser(self):
        """
        耗时......1222.376973
        :return:
        """
        for data in self._html_cursor.find():
            soup = BeautifulSoup(data['html'], 'html.parser')
            divspider = soup.find('div', class_='spider')
            if divspider is None:
                data.pop('html')
                self.log.error(data)
            row = {}
            for tag in divspider.children:
                if tag.name not in ['p', 'h2']:
                    continue
                elif tag.name == 'h2':
                    if 'name' in row:
                        self._data_cursor.save(row)
                        row.clear()
                    row['name'] = tag.text
                    continue
                elif tag.name == 'p':
                    key = reg('【[\u4e00-\u9fa5]+】', tag.text)
                    row[key] = tag.text.replace(key, '')

            self._data_cursor.save(row)

    def test(self):
        try:
            url = 'http://zhongyaofangji.com/a/aaiwan.html'
            html = self._crawler.request_get_url(url).decode('gbk')
            soup = BeautifulSoup(html, 'html.parser')
            a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z]+.html'))
            _id = 0
            for a in a_tags:
                params = {
                    '_id': _id,
                    'url': a['href'],
                    'type': 'zhongyaofangji-中药方剂'
                }
                self._urlpool.save_url(params)
                _id += 1
        except BaseException:
            pass
        finally:
            self._crawler.driver.stop_client()
