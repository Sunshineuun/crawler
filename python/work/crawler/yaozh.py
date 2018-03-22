#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import random
import re
import time
from abc import abstractmethod

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from minnie.crawler.common.Utils import getNowDate
from python.no_work.utils import mlogger
from python.no_work.utils.urlpool import URLPool
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.mongodb import MongodbCursor

logger = mlogger.get_defalut_logger('yaozhi.log', 'yaozhi')


def check_rule(html):
    """
    规则
    :return: 校验不同返回True，检验通过返回False
    """
    if html and html.__contains__('CryptoJS'):
        return 4, '被加密了，刷新'

    if html is None and html is False:
        return 1, 'html为空'

    _soup = BeautifulSoup(html, 'html.parser')

    # 可能存在tbody为空的情况，为空则该了解无效
    tbody = _soup.find('tbody')
    if tbody is None:
        return 1, 'tbody为空'

    tag = _soup.find('span', class_='toFindImg')
    if tag is None:
        return 1, 'sapn为空，单元格中无值'
    elif tag.text == '暂无权限':
        return 2, '暂无权限'
    elif tag.text != '暂无权限':
        return 0, '成功'
    else:
        return 3, '未知情况'


class yaozh(object):
    def __init__(self, ip=None):

        if not ip:
            ip = '127.0.0.1'
        self._name = self.get_name()
        self._cn_name = self.get_cn_name()
        self._users = [{
            'username': 'qiushengming@aliyun.com',
            'pwd': 'qd7qrjm3'
        }, {
            'username': '583853240@qq.com',
            'pwd': 'sy3hz3kk'
        }, {
            'username': '15210506530',
            'pwd': 'a1uj30gb'
        }]

        if not self._name:
            raise ValueError

        self._mongo = MongodbCursor(ip)
        self._urlpool = URLPool(self._mongo, self._name)
        self._crawler = Crawler()

        self._html_cursor = self._mongo.get_cursor(self._name, 'html')
        self._data_cursor = self._mongo.get_cursor(self._name, 'data')

        self.init_url()

    @abstractmethod
    def init_url(self):
        pass

    @abstractmethod
    def get_name(self):
        """
        名称标志：
            主要用于创建mongodb的数据库
        :return:
        """
        pass

    @abstractmethod
    def get_cn_name(self):
        pass

    def logout(self):
        self._crawler.driver_get_url('https://www.yaozh.com/login/logout/?backurl=http%3A%2F%2Fwww.yaozh.com%2F')

    def login(self):
        """
        登陆
        是否要切换登陆
        username = qiushengming@aliyun.com
        password = qd7qrjm3
        地址：https://www.yaozh.com/login
        :return:
        """

        self.logout()

        temp_user = random.choice(self._users)
        driver = self._crawler.get_driver()

        # Client in temporary black list
        # 建议发邮件进行报告
        if driver.find_element_by_xpath('/html/body').text == 'Client in temporary black list':
            time.sleep(100)
            return

        driver.get('https://db.yaozh.com/')
        time.sleep(10)

        driver.get('https://www.yaozh.com/login')

        username = driver.find_element_by_id('username')
        username.send_keys(temp_user['username'])
        password = driver.find_element_by_id('pwd')
        password.send_keys(temp_user['pwd'])
        login_button = driver.find_element_by_id('button')
        login_button.click()
        timeout = 2

        while True:
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/a[1]')
                break
            except NoSuchElementException:
                logger.info('登陆中，请等待')
            time.sleep(timeout)
            timeout += 2

            if timeout > 10:
                logger.error('链接超时！！')
                return False

        logger.info('登陆成功')
        return True

    def get_cookie(self):
        # 获取cookie
        cookie = ''
        for dic in self._crawler.get_driver().get_cookies():
            cookie += dic['name'] + '=' + dic['value'] + ';'
        return cookie

    def check_and_save(self, params, html):
        stat, msg = check_rule(html)
        if stat == 0:
            params['html'] = html
            params['source'] = '药智网-中药方剂'
            params['create_date'] = getNowDate()
            self._html_cursor.save(params)
            self._urlpool.update_success_url(params['url'])
        elif stat == 1:
            params['isenable'] = msg
            _id = params['_id']
            params.pop('_id')
            self._urlpool.update({'_id': _id}, params)
        elif stat == 2:
            logger.error(params['url'])
            self.logout()
            self.login()
        elif stat == 3:
            logger.info(params)

    def startup(self):
        # 登陆是否成功
        while not self.login():
            time.sleep(10)

        while not self._urlpool.empty():
            params = self._urlpool.get()
            logger.info(params['url'])
            html = None
            html_b = self._crawler.request_get_url(params['url'], header={'Cookie': self.get_cookie()})

            if not html_b:
                for i in range(10):
                    html = self._crawler.driver_get_url(params['url'])
                    self.check_and_save(params, html)
                    params = self._urlpool.get()
                time.sleep(10)
                continue
            elif html_b:
                html = html_b.decode('utf-8')

            if html is None:
                continue

            self.check_and_save(params, html)

    def parser(self):
        """
        中药方剂，中药能通用
        :return:
        """
        for i, data in enumerate(self._html_cursor.find()):
            if i % 1000 == 0:
                logger.info(i)
            soup = BeautifulSoup(data['html'], 'html.parser')
            trs = soup.find_all('tr')
            if len(trs):
                row = {'_id': data['_id'], 'url': data['url']}
                for tr in trs:
                    try:
                        row[tr.th.text] = re.sub('[\n ]', '', tr.td.span.text)
                    except AttributeError:
                        print(data['url'])

                self._data_cursor.insert(row)
            else:
                self._html_cursor.delete_one({'_id': data['_id']})
                logger.error(data['url'])
                self._urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })


class yaozh_zy(yaozh):
    def __init__(self, ip=None):
        super().__init__(ip)

    def get_name(self):
        return 'yaozh_zy'

    def get_cn_name(self):
        return '药智网-中药药材'

    def init_url(self):

        if self._urlpool.find_all_count():
            return

        url = 'https://db.yaozh.com/zhongyaocai/{code}.html'
        result_list = []
        for i in range(1600):
            result_list.append({
                'url': url.format(code=i),
                'type': self._cn_name
            })

        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')


class yaozh_zyfj(yaozh):
    def __init__(self, ip):
        super().__init__(ip)

    def get_name(self):
        return 'yaozh_zyfj'

    def get_cn_name(self):
        return '药智网-中药方剂'

    def init_url(self):
        """
        https://db.yaozh.com/fangji/10000001.html
        初始化到数据库中
        :return: 模板
        """

        if self._urlpool.find_all_count():
            return

        url = 'https://db.yaozh.com/fangji/{code}.html'
        result_list = []
        for i in range(35000):
            result_list.append({
                'url': url.format(code=10000001 + i),
                'type': '药智网-中药方剂'
            })
        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')


if __name__ == '__main__':
    # y = yaozh_zy(ip='192.168.16.113')
    # y.parser()

    y1 = yaozh_zyfj(ip='192.168.16.113')
    y1.parser()
