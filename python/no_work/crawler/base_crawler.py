#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import traceback
from abc import abstractmethod

from python.no_work.utils.common import getNowDate
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.memail import send_mail
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.urlpool import URLPool


class BaseCrawler(object):
    def __init__(self, ip=None):
        if not ip:
            ip = '127.0.0.1'

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

    def __run(self):
        try:
            while not self._urlpool.empty():
                self.startup()
        except BaseException as e:
            send_mail(traceback.format_exc())

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
    def startup(self):
        pass

    @abstractmethod
    def parser(self):
        pass

    def save_html(self, h, p):
        """
        :param h: str
        :param p: 字典
        :return:
        """
        p['html'] = h
        p['source'] = self._cn_name
        p['create_date'] = getNowDate()
        self._html_cursor.save(p)
        self._urlpool.update_success_url(p['url'])
