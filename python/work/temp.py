#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import pymongo

from minnie.crawler.common.Utils import reg
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.crawler import Crawler


def get_key(dbname):
    mongo = pymongo.MongoClient('192.168.16.113', 27017)
    cursor = mongo[dbname]['data']
    title = []
    for data in cursor.find():
        for k, v in data.items():
            if k not in title:
                title.append(k)
    print(title)
    return title


def count_url(name, ip='192.168.16.113'):
    """
    统计以抓取未抓取的url地址
    :param name:
    :param ip:
    :return:
    """
    mongo = MongodbCursor(ip)
    html_cursor = mongo.get_cursor(name, 'html')
    url_cursor = mongo.get_cursor(name, 'url')
    data_cursor = mongo.get_cursor(name, 'data')

    print('html-总数:', html_cursor.find().count())
    print('url-总数:', url_cursor.find().count())
    print('url-未抓取:', url_cursor.find({'isenable': '1'}).count())
    print('url-已抓取:', url_cursor.find({'isenable': '0'}).count())
    print('data-解析的数量', data_cursor.find().count())


def proxy():
    c = Crawler()
    c.request_get_url('https://www.yaozh.com/')
    print(1)


if __name__ == '__main__':
    # get_key('cfda')
    count_url('cfda')
    # proxy()
    pass
