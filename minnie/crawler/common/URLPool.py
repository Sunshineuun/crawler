#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
"""
url资源池
"""
import datetime
import queue


class URLPool(object):
    """
    用MongoDB存储url
    2018-3-19
        加速URL的初始化，MongoDB批量插入
    """

    def __init__(self, mongo, name):
        """
        MongodbCursor
        :param mongo:
        :param name: url组的标识
        """
        self._queue = queue.Queue(maxsize=1000)
        self.cursor = mongo.get_cursor(name, 'url')
        self.temp = []  # mongo批量插入前进行存储
        self.find_by_db()

    def put(self, params):
        """
        写入数据
        :return:
        """
        if self.cursor.find({'url': params['url']}).count() <= 0:
            params['isenable'] = '1'
            params['insert_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.insert(params)
            if not self.full():
                self._queue.put(params)

    def get(self):
        """
        获取数据
        :return:
        """
        if not self.empty():
            return self._queue.get()

        return False

    def empty(self):
        """
        :return:空返回True，非空返回False
        """
        return self.find_by_db()

    def full(self):
        """
        如果队列满了，返回True,反之False;
        q.full 与 maxsize 大小对应
        :return:
        """
        return self._queue.full()

    def find_by_db(self):
        """
        从数据库中进行加载
        :return:空返回True，非空返回False
        :return:
        """
        # 内存队列为空了，再去数据库加载否则不加载
        if self._queue.empty():
            for temp in self.cursor.find({'isenable': '1'}):
                if self.full():
                    break
                self._queue.put(temp)
        return self._queue.empty()

    def save_url(self, params):
        if type(params) is list:
            for p in params:
                if type(p) == dict:
                    p['isenable'] = '1'
                    p['insert_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif type(params) == dict:
                params['isenable'] = '1'
                params['insert_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.insert(params)

    def find_all_count(self):
        return self.cursor.find().count()

    def update(self, query, update):
        self.cursor.update(query, update)

    def update_success_url(self, url):
        if self.cursor.find({'url': url}).count() > 0:
            self.cursor.update({
                'url': url
            }, {
                '$set': {
                    'isenable': '0'
                }
            })


if __name__ == '__main__':
    """
        contains
    """
