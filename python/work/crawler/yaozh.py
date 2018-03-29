#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import random
import re
import time
from abc import abstractmethod, ABCMeta

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from minnie.crawler.common.Utils import getNowDate
from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger

logger = mlogger.get_defalut_logger('yaozhi.log', 'yaozhi')


class yaozh(BaseCrawler):
    """
        需要提交
    """
    __metaclass__ = ABCMeta

    def __init__(self, ip=None):

        super().__init__(ip)
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

    @abstractmethod
    def test(self):
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
        driver = self._crawler.driver

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

    def check_rule(self, html):
        """
        规则
        :return: 校验不同返回True，检验通过返回False
        """
        if html and html.__contains__('CryptoJS'):
            return 4, '被加密了，刷新'

        if html is None and html is False:
            return 1, 'html为空'

        soup = BeautifulSoup(html, 'html.parser')

        # 可能存在tbody为空的情况，为空则该了解无效
        tbody = soup.find('tbody')
        if tbody is None:
            return 1, 'tbody为空'

        tag = soup.find('span', class_='toFindImg')
        if tag is None:
            return 1, 'sapn为空，单元格中无值'
        elif tag.text == '暂无权限':
            return 2, '暂无权限'
        elif tag.text != '暂无权限':
            return 0, '成功'
        else:
            return 3, '未知情况'

    def get_cookie(self):
        # 获取cookie
        cookie = ''
        for dic in self._crawler.driver.get_cookies():
            cookie += dic['name'] + '=' + dic['value'] + ';'
        return cookie

    def check_and_save(self, params, html):
        stat, msg = self.check_rule(html)
        logger.info(params['url'] + " - " + msg)
        if stat == 0:
            params['html'] = html
            params['source'] = self._cn_name
            params['create_date'] = getNowDate()
            self._html_cursor.save(params)
            self._urlpool.update_success_url(params['url'])
        elif stat == 1:
            params['isenable'] = msg
            self._urlpool.update({'_id': params['_id']}, params)
        elif stat == 2:
            logger.error(params['url'])
            self.logout()
            self.login()
        elif stat == 3:
            logger.info(params)
        elif stat == 4:
            self._crawler.refresh()

    def startup(self):
        # 登陆是否成功
        while not self.login():
            time.sleep(10)

        while not self._urlpool.empty():
            params = self._urlpool.get()
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

    def _get_name(self):
        return 'yaozh_zy'

    def _get_cn_name(self):
        return '药智网-中药药材'

    def _init_url(self):

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

    def test(self):
        pass


class yaozh_zyfj(yaozh):
    def __init__(self, ip):
        super().__init__(ip)

    def _get_name(self):
        return 'yaozh_zyfj'

    def _get_cn_name(self):
        return '药智网-中药方剂'

    def _init_url(self):
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
                'type': self._cn_name
            })
        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')

    def test(self):
        pass


# 相互作用
class yaozh_interaction(yaozh):
    """
    https://db.yaozh.com/interaction
    """

    def _get_name(self):
        return 'yaozh_interaction'

    def _get_cn_name(self):
        return '药智网-相互作用'

    def _init_url(self):
        if self._urlpool.find_all_count():
            return

        url = 'https://db.yaozh.com/interaction/{code}.html'
        result_list = []
        for i in range(8000):
            result_list.append({
                'url': url.format(code=i),
                'type': self._cn_name
            })
        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')

    def check_rule(self, html):
        """
        规则
        :return: 校验不同返回True，检验通过返回False
        """
        if html and html.__contains__('CryptoJS'):
            return 4, '被加密了，刷新'

        if html is None and html is False:
            return 1, 'html为空'

        soup = BeautifulSoup(html, 'html.parser')

        # 可能存在tbody为空的情况，为空则该了解无效
        tbody = soup.find('tbody')
        if tbody is None:
            return 1, 'tbody为空'

        return 0, '成功'

    def parser(self):
        for i, data in enumerate(self._html_cursor.find()):
            soup = BeautifulSoup(data['html'], 'html.parser')
            # 药品名称
            try:
                td = soup.find('div', class_='ui-panel-content').find('td')
                if not td:
                    raise BaseException('td is null')
                drug_name = re.sub('[\n\r ]', '', td.text)
            except BaseException as exc:
                self._html_cursor.delete_one({'_id': data['_id']})
                logger.error(data['url'])
                self._urlpool.update({
                    'url': data['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })
                continue

            # 相互作用药品
            divs = soup.find_all('div', class_='m10 mb20')
            for div in divs:
                trs = div.find_all('tr')
                if len(trs):
                    row = {'url': data['url'], '药品名称': drug_name}
                    for tr in trs:
                        try:
                            row[tr.th.text] = re.sub('[\n ]', '', tr.td.text)
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

    def test(self):
        pass


# 重点用药
class yaozh_monitored(yaozh):
    def _get_name(self):
        return 'yaozh_monitored'

    def _get_cn_name(self):
        return '药智网-辅助与重点监控用药'

    def _init_url(self):
        pass

    def test(self):
        pass


if __name__ == '__main__':
    # y = yaozh_zy(ip='192.168.16.113')
    # y.parser()

    # y1 = yaozh_zyfj(ip='192.168.16.113')
    # y1.parser()

    y2 = yaozh_interaction(ip='192.168.16.113')
    y2.parser()
