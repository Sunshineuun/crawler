#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import traceback
from abc import abstractmethod

from bs4 import BeautifulSoup

from python.no_work.utils import mlogger
from python.no_work.utils.common import getNowDate
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.memail import send_mail
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.urlpool import URLPool


class BaseCrawler(object):
    def __init__(self, ip=None):
        if not ip:
            ip = '127.0.0.1'

        self.log = mlogger.mlog

        self.__name = self._get_name()
        self._cn_name = self._get_cn_name()

        if not self.__name:
            raise ValueError

        self._mongo = MongodbCursor(ip)
        self._urlpool = self.get_urlpool()
        self._crawler = Crawler()

        self._html_cursor = self.get_html_cursor()
        self._data_cursor = self.get_data_cursor()

        self.__init_url()
        self.__run()

    def get_html_cursor(self):
        return self._mongo.get_cursor(self.__name, 'html')

    def get_data_cursor(self):
        return self._mongo.get_cursor(self.__name, 'data')

    def get_urlpool(self):
        return URLPool(self._mongo, self.__name)

    def __init_url(self):
        if self._urlpool.find_all_count():
            return
        self._init_url()

    @staticmethod
    def to_soup(html):
        return BeautifulSoup(html, 'html.parser')

    def __run(self):
        try:
            while not self._urlpool.empty():
                d1 = datetime.datetime.now()
                d = self._urlpool.get()
                self.startup(d)
                d2 = datetime.datetime.now()
                self.log.info('耗时：' + str((d2 - d1).total_seconds()))
            self.parser()
        except BaseException as e:
            self.log.error(traceback.format_exc())
            send_mail(traceback.format_exc())
        finally:
            if self._crawler.driver:
                self._crawler.driver.quit()

    @abstractmethod
    def _init_url(self):
        """
        必须包含type,url这两个key值
        :return:
        """
        pass

    @abstractmethod
    def _get_name(self):
        """
        名称标志：
            主要用于创建mongodb的数据库
        :return:
        """
        pass

    @abstractmethod
    def _get_cn_name(self):
        pass

    @abstractmethod
    def startup(self, d):
        pass

    @abstractmethod
    def parser(self):
        pass

    def save_html(self, h, p1):
        """
        存储html，并且更新url状态 \n
        :param p1: 字典
        :param h: str
        :return:
        """
        p = {'html': h, 'source': self._cn_name, 'create_date': getNowDate()}
        p.update(p1)
        self._html_cursor.save(p)
        self._urlpool.update_success_url(p['url'])
