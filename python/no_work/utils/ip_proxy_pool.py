#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# IP代理池
import queue

from bs4 import BeautifulSoup

from python.no_work.utils.crawler import Crawler

check_url = 'https://hm.baidu.com/hm.gif?cc=0&ck=1&cl=24-bit&ds=1536x864&vl=767&ep=9432,3888&et=3&fl=29.0&ja=0&ln=zh-cn&lo=0&lt=1521791429&rnd=1553736295&si=65968db3ac154c3089d7f9a4cbb98c94&su=https://www.baidu.com/link?url=YTokOPSr-G1aC01053qZRiKs1sXkj9OO5heTfr03-pS&wd=&eqid=8ff59bac00003faa000000045ab4b1c0&v=1.2.30&lv=2&sn=3194'


class IPProxyPool(object):
    """
    即取即用
    """

    def __init__(self):
        self._queue = queue.Queue(maxsize=1000)
        self._page = 00
        self.crawler = Crawler()
        self.proxy_source_url = ['http://www.xicidaili.com/nn/{page}']

    def get(self):
        while True:
            if self._queue.empty():
                # 获取代理IP
                self.get_xici()
            # 验证
                # 验证成功 return
                # 验证失败 继续

    def get_xici(self):
        self._page += 1
        if self._page == 10:
            self._page = 1

        html = self.crawler.request_get_url(self.proxy_source_url[0].format(page=self._page))
        soup = BeautifulSoup(html, 'html.parser')
        tr_tags = soup.find_all('tr')
        for tr in tr_tags:
            tds = tr.find_all('td')
            self._queue.put({
                'ip': tds[1].text,
                'prot': tds[2].text,
                'type': tds[5].text,
            })

