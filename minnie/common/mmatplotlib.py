#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import random
import datetime as dtime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from minnie.common import moracle
from datetime import datetime
from matplotlib.ticker import MultipleLocator

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
cursor = moracle.OralceCursor()


def getFundName(code):
    """
    通过基金代码返回基金名称
    :param code:
    :return:
    """
    sql = 'SELECT FUND_NAME FROM FUND_OPENFUNDNETVALUE WHERE FUND_CODE = :fundCode'
    return cursor.fechall(sql, {'fundCode': code})[0][0]


def getData(code, _minDate=None, maxDate=None):
    """
    获取基金时间段内的每日净值数据
    :param code: 基金编码
    :param _minDate: is Note为max时间的前12周的日期
    :param maxDate: is Note为当天日期
    :return:
    """
    if maxDate is None:
        maxDate = datetime.now().strftime('%Y-%m-%d')

    if _minDate is None:
        delta = dtime.timedelta(weeks=12)
        _minDate = (datetime.strptime(maxDate, '%Y-%m-%d').date() - delta).strftime('%Y-%m-%d')

    data = cursor.fechall(
        "SELECT NAV,NC,FUND_DATE,FUND_CODE,NVL(GROWTHRATE, '0') GROWTHRATE FROM FUND_NET_VALUE_HISTORY WHERE FUND_CODE = :fundCode AND TO_DATE(FUND_DATE, 'yyyy-MM-dd') > TO_DATE(:minDate, 'yyyy-MM-dd') AND TO_DATE(FUND_DATE, 'yyyy-MM-dd') < TO_DATE(:maxDate, 'yyyy-MM-dd') ORDER BY FUND_DATE",
        {'fundCode': code, 'minDate': _minDate, 'maxDate': maxDate}
    )

    if not len(data):
        return [], [], ''

    # 净值
    nav = []
    # 累计净值
    nc = []
    # 日期
    date = []
    # 涨幅
    ups_downs = []
    for d in data:
        nav.append(float(d[0]))
        # nc.append(float(d[1]))
        date.append(datetime.strptime(d[2], '%Y-%m-%d').date())
        ups_downs.append(float(str(d[4]).replace('%', '')))

    return nav, date, getFundName(code), ups_downs


def showDateView(_codes, _minDate=None, maxDate=None):
    """
    数据可视化展示
    :param maxDate:
    :param _minDate:
    :param _codes: 基金编码列表
    :return:
    """
    if type(_codes) is not list:
        raise TypeError('类型错误')

    plt.figure()

    # x轴的取值范围
    # plt.xlim((-2, 4))
    # y轴的取值范围
    plt.ylim((-2, 4))

    # x轴的描述
    plt.xlabel(u'交易日期')
    # y轴的描述
    plt.ylabel(u'净值(RMB)')

    # plt.xticks(pd.date_range(data.index[0], data.index[-1], freq='1min'))  # 时间间隔
    # plt.xticks(rotation=90)

    ax = plt.gca()
    # 设置x轴显示格式及其间距
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m%d'))  # %Y%m
    ax.xaxis.set_major_locator(mdates.DayLocator())
    # 设置y轴显示格式及其间距
    ax.yaxis.set_major_locator(MultipleLocator(0.5))
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    ax.spines['bottom'].set_position(('data', 0))
    # ax.spines['left'].set_position(('data', 0))
    """
        plot方法接收需要绘制图形的数据，根据接收数据进行绘制图像。
            label-标签，图例标识
            color-绘制线条的颜色，颜色可以用CSS的颜色代码
            linewidth-线条的粗细

    """
    for code in _codes:
        nav, date, label, ups_downs = getData(code, _minDate, maxDate)
        if nav.__len__() <= 0:
            continue
        # plt.plot(date, nav, label=label)
        plt.plot(date, ups_downs, label=label + '涨幅')
        # plt.plot(date, nc, label=u'累计净值')

    # plt.gcf().autofmt_xdate()  # 自动旋转日期标记
    # 设置标题
    plt.title(minDate + '~' + maxDate + u'基金趋势图')
    """
        展示图例简介 upper left
        handles,label联合使用，修改标签的名称
    """
    plt.legend(loc='best')
    plt.show()


if __name__ == '__main__':
    # ,'161725', '070032', '110022', '000457'
    codes = ['340008', '161725', '070032', '110022', '000457']
    minDate = '2017-12-01'
    maxDate = '2018-01-01'
    showDateView(codes, minDate, maxDate)

"""
    1.怎么通过数据分析出优质基金；
    2.通过昨日数据，预测明日的涨跌情况；
    3.那些基金的涨幅受到大盘的涨幅的影响程度；
"""
