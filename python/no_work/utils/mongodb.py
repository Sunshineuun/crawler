#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
"""
1.文档中的键/值对是有序的。
2.文档中的值不仅可以是在双引号里面的字符串，还可以是其他几种数据类型（甚至可以是整个嵌入的文档)。
3.MongoDB区分类型和大小写。
4.MongoDB的文档不能有重复的键。
5.文档的键是字符串。除了少数例外情况，键可以使用任意UTF-8字符。

6.mongodb 聚合 count having count() > 1
    url.aggregate(([{'$group': {'_id': '$url', 'count': {'$sum': 1}}},
                              {"$match": {"count": {"$gt": 1}}}]),)
"""
import datetime

import pymongo


class MongodbCursor(object):
    """
    MongoDB游标
    """
    def __init__(self, ip, port=27017):
        """
        :param ip: ip地址
        :param port: 端口号，默认27017
        """
        self.client = pymongo.MongoClient(ip, port)

    def get_cursor(self, dbname, tablename):
        """
        :param dbname: 数据库名
        :param tablename: 表名
        :return:
        """
        return self.client[dbname][tablename]


if __name__ == '__main__':
    mongo = MongodbCursor('192.168.16.113')
    cursor = mongo.get_cursor('test', 'test')
    cursor.create_index()
    params = {
        'url': 'baidu.com'
    }

    d1 = datetime.datetime.now()

    for i in range(10):
        params['_id'] = i
        cursor.insert(params)

    d2 = datetime.datetime.now()
    print((d2 - d1).total_seconds())


