#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
from abc import abstractmethod

from python.no_work.utils.crawler import Crawler
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

        self._init_url()

    def get_html_cursor(self):
        return self._mongo.get_cursor(self.__name, 'html')

    def get_data_cursor(self):
        return self._mongo.get_cursor(self.__name, 'data')

    def get_urlpool(self):
        return URLPool(self._mongo, self.__name)

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
