#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler


class LianJia(BaseCrawler):
    def __init__(self, ip):
        """"""
        super().__init__(ip)
        self._url_index = 0

    def _get_cn_name(self):
        return '链家'

    def _get_name(self):
        return 'LianJia'

    def _init_url(self):
        """
        https://sh.lianjia.com/ershoufang/
        p1-p7
        :return:
        """

        self._url_index = self._urlpool.find_all_count()
        if self._url_index:
            return

        area = ['chongming', 'jinshan', 'fengxian', 'qingpu', 'hongkou', 'zhabei',
                'shanghaizhoubian', 'pudong', 'jingan', 'songjiang', 'changning',
                'yangpu', 'putou', 'baoshan', 'minhang']
        price = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7']
        url = 'https://sh.lianjia.com/ershoufang/{area}/{price}/'

        result_list = []

        index = 0
        for a in area:
            for p in price:
                html = self._crawler.driver_get_url(url.format(area=a, price=p))
                soup = BeautifulSoup(html, 'html.parser')
                div = soup.find_all('div', class_='page-box house-lst-page-box')
                max_page = 1
                if len(div):
                    a_tags = div[0].find_all('a')
                    for a_tag in a_tags:
                        if a_tag.text.isdigit() \
                                and int(a_tag.text) > max_page:
                            max_page = int(a_tag.text)

                for i in range(1, max_page + 1):
                    index += 1
                    _p = {
                        '_id': index,
                        'url': url.format(area=a, price='pg' + str(i) + p),
                        'area': a,
                        'price': p
                    }
                    result_list.append(_p)
        self._urlpool.save_url(result_list)
        self._url_index = self._urlpool.find_all_count()

    def startup(self):
        while not self._urlpool.empty():
            params = self._urlpool.get()
            html = self._crawler.driver_get_url(params['url'])
            params['html'] = html
            self._html_cursor.insert(params)
            self._urlpool.update_success_url(params['url'])

    def parser(self):
        data = {}
        print(self._html_cursor.find().count())
        for params in self._html_cursor.find():
            soup = BeautifulSoup(params['html'], 'html.parser')
            lis = soup.find_all('li', class_='clear')
            for li in lis:
                if li.a:
                    data['url'] = li.a['href']
                else:
                    print(1)
                # 单价，总价，标签，关注信息，地址信息，房屋信息，标题
                key = ['unitPrice', 'totalPrice', 'tag', 'followInfo', 'positionInfo', 'houseInfo',
                       'title']
                for k in key:
                    if li.find('div', class_=k):
                        data[k] = li.find('div', class_=k).text
                    else:
                        print(1)
                if li.find('div', class_='houseInfo'):
                    data['houseInfo1'] = li.find('div', class_='houseInfo').a.text
                else:
                    print(1)
                if li.find('div', class_='positionInfo'):
                    data['positionInfo1'] = li.find('div', class_='positionInfo').a.text
                else:
                    print(1)
                self._data_cursor.insert(data)
                data.clear()
