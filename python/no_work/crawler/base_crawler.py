#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import traceback
from abc import abstractmethod

from bs4 import BeautifulSoup

from python.no_work.utils import mlogger
from python.no_work.utils.common import getNowDate, remove_blank
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.excel import WriteXLSXCustom
from python.no_work.utils.memail import send_mail
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.urlpool import URLPool


class BaseCrawler(object):
    """
    所需要具备的功能
    1. 初始化url，需要针对不同站点进行
    2. 下载策略，需要针对不同站点进行。默认遍历链接池
    3. 脏URL过滤策略，在什么样子的情况下废弃掉该URL。默认请求失败就废弃
    4. 解析策略
        4.1 解析成功需要更新下
    5. 对外结构化策略，主要是将导入的excel中，\n
        但是这里有个问题，如果站点庞杂，所产生的属性会比较多。
    """

    def __init__(self, ip=None):
        if not ip:
            ip = '127.0.0.1'
        # 日志记录器
        self.log = mlogger.mlog

        self.__name = self._get_name()
        self._cn_name = self._get_cn_name()

        if not self.__name:
            raise ValueError("%s must have a name" % type(self).__name__)

        self._mongo = MongodbCursor(ip)

        # URL管理器
        self._urlpool = self.__get_urlpool()
        # 网页下载器
        self._crawler = Crawler()

        # 数据存储器
        self._html_cursor = self.__get_html_cursor()
        self._data_cursor = self.__get_data_cursor()
        self._html_bak = self._mongo.get_cursor(self.__name, 'htmlbak')

        self.__init_url()
        self.__run()

    def __get_html_cursor(self):
        """
        创建一个HTML存储游标，存储response\n
        :return: HTML游标
        """
        return self._mongo.get_cursor(self.__name, 'html')

    def __get_data_cursor(self):
        """
        创建DATA存储游标，解析后的数据\n
        :return: data的存储游标
        """
        return self._mongo.get_cursor(self.__name, 'data')

    def __get_urlpool(self):
        """
        创建一个URL管理器 \n
        :return: URL管理器 \n
        """
        return URLPool(self._mongo, self.__name)

    def __init_url(self):
        """
        私有方法，不被外部调用，初始化URL代码请写在`_init_url`中。
        初始化URL资源池，如果资源池有数据，则不再进行初始化。 \n
        :return: void
        """
        if self._urlpool.find_all_count():
            return
        result = self._init_url()
        self._urlpool.save_url(result)

    def __requests(self):
        """
        下载管理器
        :return:
        """
        d = None
        try:
            count = 0
            while not self._urlpool.empty():
                if count % 500 == 0:
                    self.log.info('已请求的URL数量：' + str(count))

                count += 1
                d1 = datetime.datetime.now()
                d = self._urlpool.get()

                succeed, html = self.request(d)
                if succeed:
                    self.save_html(html, d)

                d2 = datetime.datetime.now()
                self.log.info('耗时：' + str((d2 - d1).total_seconds()))
        except BaseException as e:
            msg = '' + traceback.format_exc() + '\n' + str(d)
            send_mail(msg)
            self.log.error(msg)
            self.log.error(e)

    def __parsers(self):
        """
        解析管理器
        :return:
        """
        query = {'parser_enable': {'$exists': False}}
        query.update(self.parser_target_condition())

        d = None
        try:
            for i, d in enumerate(self._html_cursor.find(query, no_cursor_timeout=True)):
                if i % 5000 == 0:
                    self.log.info('已解析数量：' + str(i))

                if self.parser(d):
                    self._html_cursor.update_one({'url': d['url']},
                                                 {'$set': {'parser_enable': '成功'}})
                else:
                    self._urlpool.update({'url': d['url']},
                                         {'$set': {'isenable': '1',
                                                   'insert_date': getNowDate()}})
                    self._html_bak.insert(d)
                    self._html_cursor.delete_one({'url': d['url']})
        except BaseException as e:
            msg = '' + traceback.format_exc() + '\n' + str(d)
            send_mail(msg)
            self.log.error(msg)
            self.log.error(e)

    def __run(self):
        """
        私有方法，不被外部调用。
        启动方法
        :return:
        """
        self.__requests()
        self.__parsers()
        if self._crawler.driver:
            self._crawler.driver.quit()

    @staticmethod
    def to_soup(html):
        """
        返回BeautifulSoup对象，详细使用见API
        http://beautifulsoup.readthedocs.io/zh_CN/v4.4.0/ \n
        :param html: 带有html标签的字符串 \n
        :return: BeautifulSoup对象 \n
        """
        return BeautifulSoup(html, 'html.parser')

    @abstractmethod
    def _init_url(self):
        """
        必须包含type,url这两个key值\n
        :return: list，资源池列表
        """
        return []

    @abstractmethod
    def _get_name(self):
        """
        名称标志：
            主要用于创建mongodb数据库的名称标识 \n
        :return:
        """
        pass

    @abstractmethod
    def _get_cn_name(self):
        """
        废弃，并没什么卵用
        :return:
        """
        pass

    @abstractmethod
    def request(self, d):
        """
        网页下载器 \n
        1. 如何使用URL\n
        2. 请求下来的响应是否正确\n
        3. 请求下来的响应是否从中提取数据\n
        以上各点交给你去处理。
        :param d: 资源
        :return: succeed标识，表示是否正确；同时返回需要存储的结果。
        """
        return True, ''

    @abstractmethod
    def parser(self, d):
        """
        结构化代码，告知爬虫，该怎么解析数据。 \n
        解析完成需要返回True or False，是否成功解析。
        :return:
        """
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

    def to_excel(self):
        """
        :return:
        """
        titles = []
        write = WriteXLSXCustom('.\\excel\\' + self._cn_name)
        for data in self._data_cursor.find():
            for k, v in data.items():
                if k not in titles:
                    titles.append(k)

        rowindex = 0
        write.write(rowindex=rowindex, data=titles)

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k in titles:
                if k in d:
                    row.append(remove_blank(str(d[k])))

            write.write(rowindex, row)
        write.close()

    def get_title(self):
        title = []
        for d in self._data_cursor.find():
            title += list(set(list(d.keys())).difference(set(title)))
        print(title)

    def parser_target_condition(self):
        """
        需要被结构化数据的查询条件，存储介质是Mogodb，所以查询条件，已mongodb的形式 \n
        :return: 一个查询条件的字典
        """
        return {}
