#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import random
import time
import traceback

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import getNowDate

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
    """
    药智网-中药方剂
    耗时：约14h
    数据量：34235条中药方剂
    """

    def __init__(self, ip='127.0.0.1'):
        self.name = 'yaozh_zyfj'
        self.pici = 0
        self.user = [{
            'username': 'qiushengming@aliyun.com',
            'pwd': 'qd7qrjm3'
        }, {
            'username': '583853240@qq.com',
            'pwd': 'sy3hz3kk'
        }, {
            'username': '15210506530',
            'pwd': 'a1uj30gb'
        }]
        self.cookie = ''

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler()

        self.html_cursor = self.mongo.get_cursor(self.name, 'html')
        self.time_cursor = self.mongo.get_cursor(self.name, 'time')
        self.data_cursor = self.mongo.get_cursor(self.name, 'data')

        self.init_url()

    def init_url(self):
        """
        https://db.yaozh.com/fangji/10000001.html
        初始化到数据库中
        :return: 模板
        """
        if self.urlpool.find_all_count():
            return
        url_template = 'https://db.yaozh.com/fangji/{code}.html'
        for i in range(35000):
            params = {
                '_id': i,
                'url': url_template.format(code=10000001 + i),
                'type': '药智网-中药方剂'
            }
            self.urlpool.save_to_db(params)
        logger.info('url初始结束！！！')

    def logout(self, driver):
        # logout
        driver.get('https://www.yaozh.com/login/logout/?backurl=http%3A%2F%2Fwww.yaozh.com%2F')

    def login(self):
        """
        登陆
        是否要切换登陆
        username = qiushengming@aliyun.com
        password = qd7qrjm3
        地址：https://www.yaozh.com/login
        :return:
        """

        temp_user = self.user[random.randint(0, len(self.user) - 1)]
        login_url = 'https://www.yaozh.com/login'
        driver = self.crawler.get_driver()

        self.logout(driver)

        driver.get('https://db.yaozh.com/')
        time.sleep(10)

        driver.get(login_url)

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
            except NoSuchElementException as e:
                logger.info('登陆中，请等待')
            time.sleep(timeout)
            timeout += 2

            if timeout > 10:
                logger.error('链接超时！！')
                return False

        logger.info('登陆成功')

        # 获取cookie
        for dic in self.crawler.get_driver().get_cookies():
            self.cookie += dic['name'] + '=' + dic['value'] + ';'

        return True

    def check_and_save(self, params, html):
        stat, msg = check_rule(html)
        if stat == 0:
            params['html'] = html
            params['source'] = '药智网-中药方剂'
            params['create_date'] = getNowDate()
            params['pici'] = self.pici
            self.html_cursor.save(params)
            self.urlpool.update_success_url(params['url'])
        elif stat == 1:
            params['isenable'] = msg
            _id = params['_id']
            params.pop('_id')
            self.urlpool.update({'_id': _id}, params)
        elif stat == 2:
            logger.error(params['url'])
            self.logout(driver=self.crawler.get_driver())
            self.login()
        elif stat == 3:
            logger.info(params)
        elif stat == 4:
            self.refresh_cookie(params)

    def request_data(self):
        """
        数据爬取模块
        2018年3月11日
        1.部分地市是没有数据
        :return:
        """
        self.pici += 1

        # 登陆是否成功
        while not self.login():
            time.sleep(10)

        while not self.urlpool.empty():
            params = self.urlpool.get()
            time_consum = []
            html = None
            _id = params['_id']
            d1 = datetime.datetime.now()
            html_b = self.crawler.request_get_url(params['url'], header={'Cookie': self.cookie})

            if not html_b:
                self.refresh_cookie(params)
                continue
            elif html_b:
                html = html_b.decode('utf-8')

            if html is None:
                continue

            d2 = datetime.datetime.now()
            time_consum.append((d2 - d1).total_seconds())

            self.check_and_save(params, html)

            d3 = datetime.datetime.now()
            time_consum.append((d3 - d2).total_seconds())
            logger.info('响应耗时，解析耗时.....' + str(time_consum))

            self.time_cursor.save({
                '_id': _id,
                'url': params['url'],
                'time': time_consum
            })

    def driver_data(self, params):
        html = self.crawler.driver_get_url(params['url'])
        self.check_and_save(params, html)

    def refresh_cookie(self, params):
        self.driver_data(params)
        # 获取cookie
        for dic in self.crawler.get_driver().get_cookies():
            self.cookie += dic['name'] + '=' + dic['value'] + ';'

    def parser(self):
        """
        解析
        结构化
        :return:
        """
        for i, data in enumerate(self.html_cursor.find()):
            if i % 1000 == 0:
                logger.info(i)
            soup = BeautifulSoup(data['html'], 'html.parser')
            tbody = soup.find('tbody')
            if tbody:
                trs = tbody.find_all('tr')
                row = {}
                for tr in trs:
                    row[tr.th.text] = tr.td.span.text

                row['_id'] = data['_id']
                row['url'] = data['url']
                self.data_cursor.insert(row)
            else:
                self.html_cursor.delete_one({'_id': data['_id']})
                logger.error(data['url'])
                self.urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })

    def test(self):
        url = 'https://db.yaozh.com/fangji/10014257.html'
        cookie = ''
        for dic in self.crawler.get_driver().get_cookies():
            cookie += dic['name'] + '=' + dic['value'] + ';'
        html = self.crawler.request_get_url(url, header={'Cookie': cookie})
        print(html)
        pass


if __name__ == '__main__':
    zyfz = yaozh('127.0.0.1')
    while not zyfz.urlpool.empty():
        try:
            zyfz.request_data()
        except BaseException as e:
            logger.error(traceback.format_exc())
    # zyfz.parser()
