#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import re
import time

from bs4 import BeautifulSoup

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import reg

logger = mlogger.get_defalut_logger('cnki_TCM.log', 'cnki_TCM')


def zgzw_recur_dic(_result, _code, _p):
    """
    数据存储，查找每个节点，看当前传入节点更像那个节点，然后转入节点下面进行查询。
    例如：12701 >> 1270101 >> 127010101
    _code在result那个节点下面
    :param _result:
    :param _code: 比对编码
    :param _p: 需要插入节点的参数
    :return: False返回上一层继续执行；True直接返回，说明找到。
    """
    if type(_result['child']) is not dict:
        return False

    # 优先匹配当前层级
    for _key, _value in _result['child'].items():
        if _code.startswith(_key):
            if zgzw_recur_dic(_value, _code, _p):
                return True
            _temp = _result['child'][_key]
            _p['child'] = {}
            _temp['child'][_code] = _p
            return True

    return False


def zgzw_recur_row(dic, s, arr=None):
    if arr is None:
        arr = []
    for key, value in dic.items():
        if value['child']:
            zgzw_recur_row(value['child'], s + value['name'] + '#', arr)

        arr.append(s + value['name'] + '#')


class cnki(object):
    """
    中国知网，中药方剂信息爬取
    方剂目录地址：http://kb.tcm.cnki.net/TCM/TCM/Guide?node=12719&dbcode=zyff
        参数：node={node}
    方剂详细列表地址：http://kb.tcm.cnki.net/TCM/TCM/NaviItem?code=127010101&wd=%25E5%25B0%258F%25E9%259D%2592%25E9%25BE%2599%25E6%25B1%25A4&stype=&pageNum=1&pageSize=1000&dbcode=zyff&navikind=
        参数：code={code}, wd={wd};code为编码，wd为方剂名称
    """

    def __init__(self, ip='127.0.0.1'):
        self.name = 'cnki_zyfj'
        self.pici = 0

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler(urlpool=self.urlpool)

        self.init_url()

    def init_url(self):
        """
        初始化urlpool
        :param urlpool:
        :return:
        """
        # 12701~12719
        url = 'http://kb.tcm.cnki.net/TCM/TCM/Guide?node={node}&dbcode=zyff'
        # 存储url到资源池中
        for i in range(1, 20):
            self.urlpool.save_to_db(params={
                'url': url.format(node=12700 + i),
                'type': '1'
            })

    def request_data(self):

        html_cursor = self.mongo.get_cursor(self.name, 'html')
        url = 'http://kb.tcm.cnki.net/TCM/TCM/NaviItem?code={code}&wd={wd}&stype=&pageNum=1&pageSize=1000&dbcode=zyff&navikind='
        while not self.urlpool.empty():
            _params = self.urlpool.get()
            _url = _params['url']
            # html = self.crawler.driver_get_url(_url, check_rule=self.check_rule)
            html = self.crawler.request_get_url(_url).decode('utf-8')
            # 存储
            if html_cursor.find({'url': _url}).count() <= 0:
                html_cursor.save({
                    'index': reg(pattern='[0-9]+', s=_url),
                    'source': '中国知网-中药方剂',
                    'url': _url,
                    'html': html,
                    'pici': '1'
                })

            _soup = BeautifulSoup(html, 'html.parser')
            tag_a = _soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))
            for a in tag_a:
                _params = {
                    'url': url.format(code=reg(pattern='[0-9]+', s=a['href']), wd=a.text),
                    'type': '2'
                }
                self.urlpool.put(_params)

    def parser_1(self):
        """
        解析数据，得到方剂类别树
        字典形式
        :return:
        """
        zyfz_zw_html_cursor = mongo.get_cursor('zyfj', 'zyfz_zw_html')
        zyfz_zw_html_result = zyfz_zw_html_cursor.find({
            'url': {
                '$regex': '127[0-9]{2}&'
            }
        })

        result = {'child': {}, 'name': '父亲节点'}
        for r in zyfz_zw_html_result:
            html = r['html']
            url = r['url']
            soup = BeautifulSoup(html, 'html.parser')
            li_tag = soup.find('li', node=reg(pattern='127[0-9]{2}', s=url))

            params = {'name': li_tag.a.text, 'child': {}}
            result['child'][li_tag['node']] = params

            # 塞入第二大类
            for tag in li_tag.find_all('li'):
                params = {'name': tag.a.text}
                zgzw_recur_dic(result, tag['value'], params)

            a_tags = soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))

            for tag in a_tags:
                _code = reg(pattern='[0-9]{7,9}', s=tag['href'])
                params = {'name': tag.text}
                zgzw_recur_dic(result, _code, params)
        return result

    def parser_2(self):
        """
        将字典树拼转换为行形式
        :return:
        """
        dic = self.parser_1()
        arr = []
        zgzw_recur_row(dic=dic['child'], s='', arr=arr)
        return arr

    @staticmethod
    def check_rule(html):
        """
        校验规则校验成功才算请求成
        :param html: 校验规则
        :return:
        """
        tag_a = []
        # 可能需要等待所以要进行请求
        time.sleep(0.5)
        _soup = BeautifulSoup(html, 'html.parser')
        tag_a += _soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))

        flag = True
        if len(tag_a) > 0 or len(_soup.find_all('a', text='>> 详情信息')) > 0 \
                or len(_soup.find_all('a')) == 0:
            flag = False

        return flag


if __name__ == '__main__':
    # 中国知网-中药方剂解析
    zgzw = cnki('192.168.16.113')
    zgzw.request_data()
