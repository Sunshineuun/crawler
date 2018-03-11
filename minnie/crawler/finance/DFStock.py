#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import json
from urllib import request

from minnie.common import moracle
from minnie.common import mlogger

logger = mlogger.get_defalut_logger('finance.log', 'finance')
cursor = moracle.OralceCursor()


class DFCF:
    """
    东方财富（DFCF）数据爬取，股票信息
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
        }
        self.opener = request.build_opener(request.HTTPHandler)
        request.install_opener(opener=self.opener)
        pass

    def request_m(self, url):
        r = request.Request(url=url, headers=self.headers)
        response = self.opener.open(r)
        return response.read().decode('UTF-8')

    def get_type(self, code=None, _type=None):
        """
        根据类型，股票代码获取股票相关数据 \n
        能抓取历史数据
        @:param code 股票代码
        @:param type 周-wk/月-mk/日-k/m60k/m30k/m15k/m5k
        :return:
        """
        if code is None or _type is None:
            raise ValueError('code or type为空值！')

        logger.info(code + '-' + _type)

        sql = 'INSERT INTO STOCK_NEW_VALUE_HISTORY (STOCK_CODE, STOCK_NAME, STOCK_DATE, OPEN_MARKET, CLOSE_MARKET, MAX_PRICE, MIN_PRICE, VOL, TRADING_VOLUME, AMPLITUDE, TYPE_K) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)'
        url = 'http://pdfm2.eastmoney.com/EM_UBG_PDTI_Fast/api/js?id={code}&TYPE={type}&rtntype=5&isCR=true'.format(
            code=code, type=_type)
        data_dic = json.loads(self.request_m(url)[1:-1])
        params = []
        for d in data_dic['data']:
            params.append(data_dic['code'])
            params.append(data_dic['name'])
            # '1990-12-19,96.05,99.98,99.98,95.79,1260,49.4万,-'
            # 时间，开盘，收盘，最高，最低，成交量，成交金额，振幅
            params += str(d).split(',')
            params.append(_type)
            cursor.executeSQLParams(sql, params)
            params.clear()

    def get_type_codes(self):
        """
        以目前股票信息库中，存在的股票抓取分时图
        :return:
        """
        sql = "SELECT STOCK_CODE||STOCK_TYPE FROM STOCK_INFO WHERE STOCK_CODE NOT IN (SELECT STOCK_CODE FROM STOCK_NEW_VALUE_HISTORY)"
        codes = cursor.fechall(sql=sql)
        for code in codes:
            self.get_type(code[0], 'k')

    def get_time_division(self, code=None):
        """
        获取指定股票代码的分时图分时图数据;\n
        目前能取到5天前的分时图，所以每周五都需要进行抓取一波 \n
        @:param code 股票代码
        :return:
        """
        if code is None:
            raise ValueError('code为空值！')
        else:
            logger.info(code)

        sql = 'INSERT INTO STOCK_TIME_DIVISION (STOCK_CODE, STOCK_NAME, STOCK_DATE, NET_VALUE, VOL, NET_VALUE_2, TEMP) VALUES (:1, :2, :3, :4, :5, :6, :7)'
        url = 'http://pdfm2.eastmoney.com/EM_UBG_PDTI_Fast/api/js?id={code}&TYPE={type}&rtntype=5&isCR=false'.format(
            code=code, type='T3')
        data_dic = json.loads(self.request_m(url)[1:-1])
        params = []
        for d in data_dic['data']:
            params.append(data_dic['code'])
            params.append(data_dic['name'])
            # '1990-12-19,96.05,99.98,99.98,95.79,1260,49.4万,-'
            # 时间，开盘，收盘，最高，最低，成交量，成交金额，振幅
            params += str(d).split(',')
            cursor.executeSQLParams(sql, params)
            params.clear()

    def get_time_division_codes(self):
        """
        以目前股票信息库中，存在的股票抓取分时图 \n
        datetime.datetime.now().strftime('%Y-%m-%d')
        :return:
        """
        sql = "SELECT STOCK_CODE||STOCK_TYPE FROM STOCK_INFO WHERE STOCK_CODE NOT IN (SELECT STOCK_CODE FROM STOCK_TIME_DIVISION WHERE TO_DATE(STOCK_DATE, 'yyyy-MM-dd hh24:mi') > to_date(:nowData, 'yyyy-MM-dd hh24:mi'))"
        codes = cursor.fechall(sql=sql, params={'nowData': '2018-01-05'})
        for code in codes:
            self.get_time_division(code[0])

    def get_stock_info_day(self):
        """
        股票每日的信息爬取
        :return:
        """

        sql = 'INSERT INTO STOCK_INFO_DAY (STOCK_TYPE, STOCK_CODE, STOCK_NAME, NOW_PRICE, UPS_DOWNS_PRICE, UPS_DOWNS_PCT, AMPLITUDE, VOL, TRADING_VOLUME, YESTERDAY_CLOSED, THIS_OPEN, MAX_VALUE, MIN_VALUE, REMARK) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)'
        """
            pageSize = 3500
        """
        url = 'http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=C._A&sty=FCOIATA&sortType=C&sortRule=-1&page=1&pageSize={pageSize}&token={token}'.format(
            pageSize=3500, token='7bc05d0d4c3c22ef9fca8c2a912d779c')
        _data = self.request_m(url)[3:-3].split('","')
        params = []
        for d in _data:
            # 2，股票代码，股票名称，最新价，涨跌额，涨跌幅，振幅，成交量，成交额，昨收，今日开，最高，最低，备注
            params += str(d).split(',')[0:13]
            params.append(d)
            cursor.executeSQLParams(sql, params)
            params.clear()


if __name__ == '__main__':
    dfcf = DFCF()
    dfcf.get_time_division_codes()
