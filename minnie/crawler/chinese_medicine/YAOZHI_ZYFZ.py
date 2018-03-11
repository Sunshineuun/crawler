#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import random
import time

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from minnie.common import mlogger
from minnie.crawler.common.Crawler import Crawler
from minnie.crawler.common.MongoDB import MongodbCursor
from minnie.crawler.common.URLPool import URLPool
from minnie.crawler.common.Utils import getNowDate

logger = mlogger.get_defalut_logger('YAZHI_ZYFZ.log', 'YAZHI_ZYFZ')


def check_rule(html):
    """
    规则
    :return:
    """
    _soup = BeautifulSoup(html, 'html.parser')
    tag = _soup.find('span', class_='toFindImg')
    if tag is not None and tag.text == '暂无权限':
        return True
    elif tag is None:
        return False
    elif tag is not None and tag.text is not None:
        return False
    else:
        return False


class YAZHI_ZYFZ(object):
    """
    药智网-中药方剂
    """

    def __init__(self, url_pool, mongo):
        self.urlpool = url_pool
        self._mongo = mongo
        self.init_url(urlpool)
        self.crawler = Crawler(urlpool=urlpool, mongo=mongo)
        self.user = [{
            'username': 'qiushengming@aliyun.com',
            'pwd': 'qd7qrjm3'
        }, {
            'username': '583853240@qq.com',
            'pwd': 'sy3hz3kk'
        }]

    def logout(self, driver):
        # logout
        logout = driver.find_element_by_link_text('退出')
        logout.click()

    def login(self):
        """
        登陆
        是否要切换登陆
        username = qiushengming@aliyun.com
        password = qd7qrjm3
        地址：https://www.yaozh.com/login
        :return:
        """

        temp_user = self.user[random.randint(0, len(self.user)-1)]
        login_url = 'https://www.yaozh.com/login'
        driver = self.crawler.get_driver()
        driver.get(login_url)

        username = driver.find_element_by_id('username')
        username.send_keys(temp_user['username'])
        password = driver.find_element_by_id('pwd')
        password.send_keys(temp_user['pwd'])
        login_button = driver.find_element_by_id('button')
        login_button.click()
        while True:
            try:
                driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/a[1]')
                break
            except NoSuchElementException as e:
                logger.info('登陆中，请等待')
            time.sleep(2)

        logger.info('登陆成功')

    def start_crawler(self):
        """
        数据爬取模块
        2018年3月11日
        1.部分地市是没有数据
        :return:
        """
        self.login()
        yzw_cursor = self._mongo.get_cursor('zyfj', 'yzw_html')
        yzw_cursor.ensure_index('url', unique=True)
        error_count = 0
        while not urlpool.empty():
            params = urlpool.get()
            html = self.crawler.driver_get_url(params['url'], check_rule=check_rule)
            if html is not None and html is not False:

                params['html'] = html
                params['source'] = '药智网-中药方剂'
                params['create_date'] = getNowDate()
                yzw_cursor.insert(params)
            else:
                logger.error(params['url'])
                # self.logout(driver=self.crawler.get_driver())
                self.login()
                # error_count += 1
                # time.sleep(10)

            if error_count > 10:
                time.sleep(10)
                # 发送邮件进行通知

    def parser(self):
        """
        解析
        结构化
        :return:
        """
        html_cursor = self._mongo.get_cursor('zyfj_data', 'yzw')
        data_cursor = self._mongo.get_cursor('zyfj_data', 'yzw')

        id = 0
        for html in html_cursor.find():
            _soup = BeautifulSoup(html, 'html.parser')
            tbody = _soup.find('tbody')
            trs = tbody.find_all('tr')
            row = {}
            for tr in trs:
                row[tr.th.text] = tr.td.span.text

            row['_id'] = id
            data_cursor.insert(row)

            id += 1

    def init_url(self, url_pool):
        """
        https://db.yaozh.com/fangji/10000001.html
        初始化到数据库中
        :return: 模板
        """
        if url_pool.find_all_count():
            return
        url_template = 'https://db.yaozh.com/fangji/{code}.html'
        for i in range(34235):
            params = {
                '_id': i,
                'url': url_template.format(code=10000001 + i),
                'type': '药智网-中药方剂'
            }
            url_pool.save_to_db(params)
        logger.info('url初始结束！！！')


if __name__ == '__main__':
    mongo = MongodbCursor('192.168.16.113')
    urlpool = URLPool(mongo, 'yzw_zyfj')
    zyfz = YAZHI_ZYFZ(urlpool, mongo)
    zyfz.start_crawler()
