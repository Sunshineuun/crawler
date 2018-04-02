#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import datetime
import random
import re
import time
from abc import abstractmethod, ABCMeta

from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger
from python.no_work.utils.common import getNowDate, reg

logger = mlogger.get_defalut_logger('yaozhi.log', 'yaozhi')
BASE_DOMAIN = 'https://db.yaozh.com'


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
        self._crawler.driver_get_url(
            'https://www.yaozh.com/login/logout/?backurl=http%3A%2F%2Fwww.yaozh.com%2F')

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

    def save_html(self, h, p):
        """

        :param h: str
        :param p: 字典
        :return:
        """
        p['html'] = h
        p['source'] = self._cn_name
        p['create_date'] = getNowDate()
        self._html_cursor.save(p)
        self._urlpool.update_success_url(p['url'])

    def check_and_save(self, params, html):
        stat, msg = self.check_rule(html)
        logger.info(params['url'] + " - " + msg)
        if stat == 0:
            self.save_html(html, params)
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
            html_b = self._crawler.request_get_url(params['url'],
                                                   header={'Cookie': self.get_cookie()})

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
        """
        按照时间查找
        https://db.yaozh.com/monitored?p=1&pageSize=30&time=2016-01
        :return:
        """
        if self._urlpool.find_all_count():
            return

        url = 'https://db.yaozh.com/monitored?p=1&pageSize=30&time={date}'
        result_list = []
        end = datetime.datetime.now()
        year = 2015
        month = 8
        while True:
            month += 1
            if month > 12:
                month = 1
                year += 1
            start = datetime.datetime(year, month, 1)
            if start > end:
                break
            result_list.append({
                'url': url.format(date=start.strftime('%Y-%m')),
                'type': self._cn_name
            })
        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')

    def startup(self):
        city = ['青海省人民医院', '青海省青海大学附属医院',
                '青海省青海红十字医院', '青海省省藏医院', '青海省省妇女儿童医院', '青海省省中医院',
                '青海省西宁市第一人民医院']
        while not self._urlpool.empty():
            # 获取参数
            params = self._urlpool.get()
            # 加载页面
            html = self._crawler.driver_get_url(params['url'])
            # soup化
            soup = BeautifulSoup(html, 'html.parser')
            # 获取数据所在位置，进行验证确认。
            tbody = soup.find_all('tbody')
            # 校验：校验通过存储数据，继续；校验失败，跳过
            if tbody and len(tbody) >= 1:
                # 存储详情页链接，直接存储data中去
                for tr in tbody[0].find_all('tr'):
                    p = {
                        'date': getNowDate(),
                        'url_': params['url']
                    }
                    a = tr.find('a')
                    if a['href'].__contains__(BASE_DOMAIN):
                        url = a['href']
                    else:
                        url = BASE_DOMAIN + a['href']
                    p['url'] = url
                    p['药物名称'] = tr.find('th').text

                    tds = tr.find_all('td')[0:5]
                    p['药物剂型'] = tds[0].text
                    p['地域机构'] = tds[1].text
                    p['日期'] = tds[2].text
                    p['监管级别'] = tds[3].text
                    p['政策文件'] = tds[4].text

                    self._data_cursor.insert(p)
                    # self._urlpool.put(params)
                self.save_html(h=html, p=params)
            else:
                self._urlpool.update({'url': params['url']}, {'isenable': '无效链接'})
                continue

            # 如果是第一页的话，需要检测是否还有下一页
            page = soup.find('span', class_='total-nums')
            if params['url'].__contains__('?p=1&') and page:
                count = int(reg('[0-9]+', page.text))
                url = params['url']
                if count > 210:
                    logger.info(url)
                    page = 8
                else:
                    page = count // 30 + 2
                # 获取page_count，整除+2，因为range[大于等于, 小于]，整除是向下取整
                for i in range(2, page):
                    self._urlpool.put({
                        'url': url.replace('p=1', 'p=' + str(i)),
                        'type': self._cn_name
                    })

    def test(self):
        pass
