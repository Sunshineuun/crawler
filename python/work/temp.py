#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import csv
import datetime

import pymongo

from python.no_work.crawler.realty import LianJia
from python.no_work.utils.excel import WriteXLSX
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.crawler import Crawler
from python.work.crawler.yaozh import yaozh_monitored, yaozh_zy, yaozh_unlabeleduse

mongo = pymongo.MongoClient('192.168.5.94', 27017)


def get_key(dbname):
    cursor = mongo[dbname]['data']
    title = []
    for data in cursor.find():
        for k, v in data.items():
            if k not in title:
                title.append(k)
    print(title)
    return title


def count_url(name):
    """
    统计以抓取未抓取的url地址
    :param name:
    :param ip:
    :return:
    """
    html_cursor = mongo[name]['html']
    url_cursor = mongo[name]['url']
    data_cursor = mongo[name]['data']

    print('html-总数:', html_cursor.find().count())
    print('url-总数:', url_cursor.find().count())
    print('url-未抓取:', url_cursor.find({'isenable': '1'}).count())
    print('url-已抓取:', url_cursor.find({'isenable': '0'}).count())
    print('data-解析的数量', data_cursor.find().count())


def yaozh_monitored_count():
    """
    统计每个月的数量
    :return:
    """
    cursur = mongo['yaozh_monitored']['data']
    end = datetime.datetime.now()
    year = 2015
    month = 8
    while True:
        month += 1
        if month > 12:
            month = 1
            year += 1
        start = datetime.datetime(year, month, 1)
        print(
            start.strftime('%Y-%m'),
            cursur.find({'日期': {'$regex': start.strftime('%Y-%m')}}).count()
        )
        if start > end:
            break


if __name__ == '__main__':
    """
    """
    # yaozh_monitored_count()
    # y = yaozh_zy(ip='192.168.5.94')
    # y.parser()
    # w = WriteXLSX(path='D://Temp//药智网_中药药材_yaozh_zy.xlsx')
    # w.write('yaozh_zy', 'data')

    # y1 = yaozh_zyfj(ip='192.168.16.113')
    # y1.parser()

    # y2 = yaozh_interaction(ip='192.168.16.113')
    # y2.parser()
    # w = WriteXLSX(path='D://Temp//药智网_药品相互作用_interaction.xlsx')
    # w.write('yaozh_interaction', 'data')

    # y3 = yaozh_monitored('192.168.5.94')
    # y3.startup()
    # w = WriteXLSX(path='D://Temp//药智网_辅助与重点监控用药_yaozh_monitored.xlsx')
    # w.write('yaozh_monitored', 'data')

    y4 = yaozh_unlabeleduse('192.168.5.94')
    y4.startup()

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
