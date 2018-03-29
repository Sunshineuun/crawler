#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import re

from bs4 import BeautifulSoup

from minnie.crawler.common.Utils import reg
from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger
from python.no_work.utils.urlpool import URLPool
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.mongodb import MongodbCursor

logger = mlogger.get_defalut_logger('./log/zhongyoo.log', 'zhongyoo')


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
            logger.info('已初始化....重新初始化请清空数据库')
            return
        logger.info('url初始开始！')
        url = 'http://zhongyaofangji.com/all.html'
        logger.info('请求开始......')
        html = self._crawler.request_get_url(url)
        # logger.info('获取编码......')
        # from_encoding = chardet.detect(html)

        logger.info('对象转换开始......')
        soup = BeautifulSoup(html, 'html.parser', from_encoding='gb2312')
        print(soup.original_encoding)

        logger.info('获取标签开始......')
        a_tags = soup.find_all('a', href=re.compile('http://zhongyaofangji.com/[a-z]/[a-z0-1_]+.html'))

        logger.info('遍历存储开始......')
        _id = 0
        for a in a_tags:
            params = {
                '_id': _id,
                'url': a['href'],
                'type': self._cn_name
            }
            self._urlpool.save_url(params)
            _id += 1
        logger.info('url初始结束！')

    def startup(self):
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
                        logger.error(error)

                if not html_str:
                    continue

                # soup = BeautifulSoup(html_str, 'html.parser', from_encoding='gb2312')
                data['html'] = html_str
                self._html_cursor.save(data)
                self._urlpool.update_success_url(data['url'])
                logger.info('耗时.....' + str((datetime.datetime.now() - d1).total_seconds()))
            except BaseException as e:
                logger.error(data['url'])
                logger.error(e)
                pass

    def parser(self):
        """
        耗时......1222.376973
        :return:
        """
        for data in self._html_cursor.find():
            soup = BeautifulSoup(data['html'], 'lxml')
            row = {
                '_id': data['_id'],
                'url': data['url'],
                'name': soup.find('a', href=re.compile(data['url'][25:]+'#+')).text
            }
            p_tags = soup.find_all('p')
            if not len(p_tags):
                self._urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })
                continue

            for p in p_tags:
                try:
                    tag = reg('【[\u4e00-\u9fa5]+】', p.text)
                    row[tag] = p.text.replace(tag, '')
                except:
                    pass

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


if __name__ == '__main__':
    # TODO 修改URL存储的地址
    zyfz = zhongyaofangji('192.168.16.113')
    zyfz._init_url()
