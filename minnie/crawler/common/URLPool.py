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
    """

    def __init__(self, mongo, name):
        """
        MongodbCursor
        :param mongo:
        :param name: url组的标识
        """
        self.url_name = 'url_' + name
        self._queue = queue.Queue(maxsize=1000)
        self.cursor = mongo.get_cursor('minnie', self.url_name)
        self.find_db()
        print('urlpool init!')

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
        获取数据，
        1.队列不为空返回数据
        2.队列为空，则从数据库中取数据，如果取到数据则返回数据
        3.以上两步都没有返回数据则返回false
        :return:
        """
        if self.empty() is False:
            return self._queue.get()

        if not self.find_db():
            return self._queue.get()

        return False

    def empty(self):
        """
        :return:空返回True，非空返回False
        """
        for temp in self.cursor.find({'isenable': '1'}).limit(2000):
            if self.full():
                break
            self._queue.put(temp)
        return self._queue.empty()

    def full(self):
        """
        如果队列满了，返回True,反之False;
        q.full 与 maxsize 大小对应
        :return:
        """
        return self._queue.full()

    def find_db(self):
        for temp in self.cursor.find({'isenable': '1'}).limit(2000):
            if self.full():
                break
            self._queue.put(temp)
        return not self.empty()

    def save_to_db(self, params):
        params['isenable'] = '1'
        params['insert_date'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.insert(params)

    def find_all_count(self):
        return self.cursor.find().count()
