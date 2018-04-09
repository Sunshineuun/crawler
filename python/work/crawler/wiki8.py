#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 医学百科
from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler


class disease(BaseCrawler):
    def __init__(self, ip):
        self.domain = 'https://www.wiki8.com'
        super().__init__(ip)

    def _get_name(self):
        return 'wiki8_disease'

    def _get_cn_name(self):
        return '医学百科-疾病'

    def _init_url(self):
        url = 'https://www.wiki8.com/Categorize/%E7%96%BE%E7%97%85_{page}.html'
        result = []
        for p in range(1, 20):
            result.append({
                'url': url.format(page=p),
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self):
        d = self._urlpool.get()
        res = self._crawler.get(d['url'])
        if res.status_code != 200:
            return

        if d['tree'] == 0:
            soup = self.to_soup(res.text)
            a_tags = soup.find('ul', class_='cateList').find_all('a')
            result = []
            for a in a_tags:
                result.append({
                    'url': self.domain + a['href'],
                    'type': self._cn_name,
                    'tree': 1
                })
            self._urlpool.save_url(result)

        elif d['tree'] == 1:
            # 这里是否需要校验一下，请求的数据是否有效
            pass
        self.save_html(res.text, d)

    def parser(self):
        pass
