#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
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
    # 可能存在tbody为空的情况，为空则该了解无效
    # tbody = _soup.find('tbody')

    tag = _soup.find('span', class_='toFindImg')
    if tag is not None and tag.text == '暂无权限':
        return True
    elif tag is None:
        return False
    elif tag is not None and tag.text is not None:
        return False
    else:
        return False


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

        self.mongo = MongodbCursor(ip)
        self.urlpool = URLPool(self.mongo, self.name)
        self.crawler = Crawler(urlpool=self.urlpool, mongo=self.mongo)

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
        try:
            logout = driver.find_element_by_link_text('退出')
            logout.click()
        except NoSuchElementException as e:
            logger.error(e)

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
        return True

    def request_data(self):
        """
        数据爬取模块
        2018年3月11日
        1.部分地市是没有数据
        :return:
        """
        self.pici += 1

        while not self.login():
            time.sleep(10)

        yzw_cursor = self.mongo.get_cursor(self.name, 'html')
        error_count = 0
        while not self.urlpool.empty():
            params = self.urlpool.get()
            html = self.crawler.driver_get_url(params['url'], check_rule=check_rule)
            if html is not None and html is not False:

                params['html'] = html
                params['source'] = '药智网-中药方剂'
                params['create_date'] = getNowDate()
                params['pici'] = self.pici
                yzw_cursor.save(params)
            else:
                logger.error(params['url'])
                self.logout(driver=self.crawler.get_driver())
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
        html_cursor = self.mongo.get_cursor(self.name, 'html')
        data_cursor = self.mongo.get_cursor(self.name, 'data')

        for i, data in enumerate(html_cursor.find()):
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
                data_cursor.insert(row)
            else:
                html_cursor.delete_one({'_id': data['_id']})
                logger.error(data['url'])
                self.urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })


def getcount():
    """
    待处理
    :return:
    """
    mongo = MongodbCursor('192.168.16.113')
    cursor = mongo.get_cursor('minnie', 'url_yzw_zyfj')
    print(
        cursor.find({'isenable': '1'}).count()
    )


if __name__ == '__main__':
    zyfz = yaozh('192.168.16.113')
    while not zyfz.urlpool.empty():
        try:
            zyfz.request_data()
            zyfz.parser()
        except:
            pass
