#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import random
import re

from minnie.crawler.common.MongoDB import MongodbCursor


def reg(pattern, s):
    """
    [\u4e00-\u9fa5]+ - 匹配中文
    :param pattern: 正则表达式
    :param s: 匹配对象
    :return: 匹配的第一条数据
    """
    # re.search(re.compile(pattern), s).group(0)
    ma = re.search(re.compile(pattern), s)
    if ma is not None:
        return ma.group(0)
    return ''


def getNowDate():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    """"""
    mongo = MongodbCursor('192.168.16.113')
    cursor = mongo.get_cursor('zyfj', 'yzw_html')
    cursor1 = mongo.get_cursor('bak', 'zyfj_yzw_html')
    for i, d in enumerate(cursor.find()):
        cursor1.insert(d)
