#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import csv
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

        # 可能存在tbody为空的情况，为空则该了解无效，其实是请求失败的一种表现
        tbody = soup.find('tbody')
        if tbody is None:
            return 3, 'tbody为空'

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
            html_b = self._crawler.driver_get_url(params['url'])

            if not html_b:
                for i in range(10):
                    html = self._crawler.driver_get_url(params['url'])
                    self.check_and_save(params, html)
                    params = self._urlpool.get()
                time.sleep(10)
                continue
            elif html_b:
                html = html_b

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
                        # logger.error(data['url'])
                        pass

                self._data_cursor.save(row)
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
        for i in range(1700):
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
                            logger.error(data['url'])

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
    """
    比较难，将数据爬取全。
    问题说明：
        1.地址没有规律不能按照规则去查找
        2.通过'发文时间'条件进行查找，但是查找的每个月份，可能数据超过210条，这样的话，超过部分就无法获取了。
        3.通过增加特殊条件进行处理，需要人工介入
    """

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
                'url': 'https://db.yaozh.com/monitored?p=1&pageSize=30&time={date}'.format(
                    date=start.strftime('%Y-%m')),
                'type': self._cn_name
            })

        # 2017-12 河南省单独查找
        result_list.append({
            'url': 'https://db.yaozh.com/monitored?p=1&area=河南省&pageSize=30&time=2017-12',
            'type': self._cn_name
        })

        # 2016-12 分地市查找
        city = ['青海红十字医院', '省中医院', '省藏医院', '省妇女儿童医院', '省心脑血管病医院', '省第四人民医院', '西宁市第一人民医院', '西宁市市第二人民医院',
                '互助县人民医院']
        for c in city:
            result_list.append({
                'url': 'https://db.yaozh.com/monitored?p=1&area={area}&pageSize=30&time=2016-12'.format(area=c),
                'type': self._cn_name
            })

        # 2018-01 分地市查找
        city = ['郑州市', '洛阳市', '开封市', '新乡市', '平顶山市', '南阳市', '安阳市', '焦作市', '驻马店市', '商丘市',
                '濮阳市', '信阳市', '许昌市', '三门峡市', '漯河市', '周口市', '鹤壁市', '济源市', '河南省人民医院', '河南省胸科医院',
                '河南省肿瘤医院', '阜外华中心血管病医院', '郑州大学第一附属医院', '郑州大学第二附属医院', '郑州大学第三附属医院',
                '郑州大学第五附属医院', '河南省直属机关第二门诊部', '河南省直第三人民医院', '河南省省立医院', '河南省职工医院',
                '河南科技大学第一附属医院', '河南医学高等专科学校附属医院', '新乡医学院第一附属医院', '河南省精神病医院（新乡医学院第二附属医院）',
                '新乡医学院第三附属医院', '河南大学第一附属医院', '河南大学淮河医院', '黄河水利委员会黄河中心医院', '河南省老干部康复医院',
                '兰考县', '固始县', '永城市', '新蔡县', '汝州市', '滑县', '邓州市', '长垣县', '鹿邑县']
        for c in city:
            result_list.append({
                'url': 'https://db.yaozh.com/monitored?p=1&area={area}&pageSize=30&time=2018-01'.format(area=c),
                'type': self._cn_name
            })

        self._urlpool.save_url(result_list)
        logger.info('url初始结束！！！')

    def startup(self):
        while not self._urlpool.empty():
            # 获取参数
            params = self._urlpool.get()
            # 加载页面
            html = self._crawler.driver_get_url(params['url'])
            time.sleep(0.5)
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
                params['isenable'] = '无效链接'
                # self._urlpool.update({'_id': params['_id']}, params)
                logger.info(params['url'])
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


# 超说明书用药
class yaozh_unlabeleduse(yaozh):
    def _init_url(self):
        if self._urlpool.find_all_count():
            return

        url = 'https://db.yaozh.com/unlabeleduse?p=1&name={name}&pageSize=30'
        result_list = []

        csv_reader = csv.reader(open('D:\Temp\药物成分表.csv', encoding='utf-8'))
        for row in csv_reader:
            result_list.append({
                'url': url.format(name=row[0]),
                'type': self._get_cn_name()
            })
        self._urlpool.save_url(result_list)

    def _get_name(self):
        return 'yaozh_unlabeleduse'

    def _get_cn_name(self):
        return '药智网_超说明书用药'

    def startup(self):
        # 登陆是否成功
        while not self.login():
            time.sleep(10)

        index = 0
        while not self._urlpool.empty():
            index += 1
            if index % 500 == 0:
                count = self._urlpool.cursor.find({'url_': {'$exists': 'true'}}).count()
                logger.info('获取数量：' + str(count))
                if count == 1658:
                    break
                self._crawler.update_proxy()
                self.login()
                time.sleep(4)
            # 获取参数
            params = self._urlpool.get()
            # 加载页面
            html = self._crawler.driver_get_url(params['url'])
            time.sleep(0.5)
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

                    tds = tr.find_all('td')[0:2]
                    p['超说明书适应症'] = tds[0].text
                    p['批准适应症'] = tds[1].text

                    self._urlpool.save_url(p)
                self.save_html(h=html, p=params)
            else:
                # 无效链接
                params['isenable'] = '3'
                self._urlpool.update({'_id': params['_id']}, params)
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

    def startup2(self):
        # 登陆是否成功
        while not self.login():
            time.sleep(10)

        for params in self._urlpool.cursor.find({'url_': {'$exists': 'true'}}):
            # 加载页面
            html = self._crawler.driver_get_url(params['url'])
            time.sleep(0.5)
            # soup化
            soup = BeautifulSoup(html, 'html.parser')
            # 获取数据所在位置，进行验证确认。
            tbodys = soup.find_all('tbody')
            # 校验：校验通过存储数据，继续；校验失败，跳过
            if tbodys and len(tbodys) >= 1:
                for tbody in tbodys[1:3]:
                    p = {
                        'date': getNowDate(),
                        'url': params['url'],
                        '药物名称': params[''],
                        '超说明书适应症': params['超说明书适应症'],
                        '批准适应症': params['超说明书适应症'],
                    }
                    for tr in tbody.find_all('tr'):
                        p[tr.th.text] = tr.td.text
                    self._data_cursor.insert(p)
                self.save_html(h=html, p=params)
            else:
                # 无效链接
                params['isenable'] = '4'
                self._urlpool.update({'_id': params['_id']}, params)
                continue

    def test(self):
        pass
