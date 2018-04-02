#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import pymongo

from python.no_work.utils.excel import WriteXLSX
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.crawler import Crawler
from python.work.crawler.yaozh import yaozh_monitored


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


def count_url(name, ip='192.168.5.94'):
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
    html = c.request_get_url(
        'https://sh.lianjia.com/api/newhouserecommend?type=1&query=https://sh.lianjia.com/ershoufang/pg3/').decode(
        'utf-8')
    print(1)


if __name__ == '__main__':
    # y = yaozh_zy(ip='192.168.16.113')
    # y.parser()

    # y1 = yaozh_zyfj(ip='192.168.16.113')
    # y1.parser()

    # y2 = yaozh_interaction(ip='192.168.16.113')
    # y2.parser()

    y3 = yaozh_monitored('192.168.5.94')
    y3.startup()

    # w = WriteXLSX(path='D://Temp//CFDA.xlsx')
    # w.write('cfda', 'data')

    # get_key('cfda')
    # count_url('cfda1')
    # count_url('cfda')
    # proxy()
    # content2 = []
    # mongo = MongodbCursor('192.168.16.113')
    # cursor = mongo.get_cursor('zhongyaofangji', 'data')
    # for data in cursor.find():
    #     t = re.sub('《.*》', '', data['name'])
    #     if t not in content2:
    #         content2.append(t)
    #
    # result = []
    # for d in readFile('D:/1.txt').split(','):
    #     if d not in content2:
    #         result.append(d)
    # print(
    #     re.sub('《.*》', '', '《111》222')
    # )
