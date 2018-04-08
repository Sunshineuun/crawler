#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 医脉通
import re
from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler


class disease(BaseCrawler):
    """
    python填坑
    1.__init__:方法在继承时,定义完自己要定义的属性,然后再调用super.__init__.
    不然自定属性不生效
    """

    def __init__(self, ip):
        self.__domain = 'http://disease.medlive.cn'
        super().__init__(ip)

    def _get_cn_name(self):
        return '医脉通-疾病'

    def _get_name(self):
        return 'medlive_disease'

    def _init_url(self):
        if self._urlpool.find_all_count():
            return
        result = []
        clinical_center = self._get_clinical_center()
        for d in clinical_center:
            res = self._crawler.get(d['url'])
            if not res:
                continue
            soup = BeautifulSoup(res.text, 'html.parser')
            atags = soup.find_all('a', href=re.compile('/gather/[0-9a-zA-Z%]+'))

            for a in atags:
                result.append({
                    'url': self.__domain + a['href'],
                    'name': a['title'],
                    'state': a.span.text,
                    'type': self._get_cn_name(),
                    'clinical_center': d['clinical_center']
                })

        self._urlpool.save_url(result)

    def _get_clinical_center(self):
        """
        http://disease.medlive.cn/wiki/list/171，获取科室
        :return: 科室地址列表
        """
        url = 'http://disease.medlive.cn/wiki/list/171'
        result = []
        res = self._crawler.get(url)
        if not res:
            raise ValueError('科室地址获取失败')

        soup = BeautifulSoup(res.text, 'html.parser')
        div = soup.find('div', class_='sortCont')
        atags = div.find_all('a')
        for a in atags:
            result.append({
                'url': self.__domain + a['href'],
                'clinical_center': a.text
            })
        return result

    def startup(self):
        """
        (简介,101_0),(名称与编码,102_0),(历史,103_0),(缩略语表,105_0),
        (定义,201_0),(流行病学,202_0),(病因,203_0),(病理解剖,204_0),(病理生理,205_0),(分类分型,206_0)
        (预防,301_0),(筛检,302_0)
        (问诊与查体,401_0),(疾病演变,402_0),(辅助检查,403_0),(并发症,404_0),(诊断标准,405_0),(诊断程序,406_0),(鉴别诊断,407_0)
        (治疗目标,501_0),(治疗细则,502_0),(管理与监测,503_0),(治疗程序,504_0),(治疗进展,505_0),(护理与照顾,506_0)
        (随访要点,601_0),(预后,602_0),(患者教育,603_0),
        (诊疗指南,701),(临床路径,702),(病例,703),(临床问题,704),
        (参考文献,801),(网络资源,802_0),(推荐文献,803),(课件,804),
        :return:
        """
        exclude_keys = ['精要', '致谢', '图片', '课件', '病例', '临床路径', '参考文献', '网络资源', '推荐文献']
        keys = [('简介', '101_0'), ('名称与编码', '102_0'), ('历史', '103_0'), ('缩略语表', '105_0'),
                ('定义', '201_0'), ('流行病学', '202_0'), ('病因', '203_0'), ('病理解剖', '204_0'), ('病理生理', '205_0'),
                ('分类分型', '206_0'),
                ('预防', '301_0'), ('筛检', '302_0'),
                ('问诊与查体', '401_0'), ('疾病演变', '402_0'), ('辅助检查', '403_0'), ('并发症', '404_0'), ('诊断标准', '405_0'),
                ('诊断程序', '406_0'), ('鉴别诊断', '407_0'),
                ('治疗目标', '501_0'), ('治疗细则', '502_0'), ('管理与监测', '503_0'), ('治疗程序', '504_0'), ('治疗进展', '505_0'),
                ('护理与照顾', '506_0'),
                ('随访要点', '601_0'), ('预后', '602_0'), ('患者教育', '603_0'),
                ('诊疗指南', '701'), ('临床路径', '702'), ('病例', '703'), ('临床问题', '704'),
                ('参考文献', '801'), ('网络资源', '802_0'), ('推荐文献', '803'), ('课件', '804'), ]

        while not self._urlpool.empty():
            d = self._urlpool.get()
            data = {}
            data.update(d)
            html = {}
            html.update(d)

            res = self._crawler.get(d['url'])
            if not res:
                continue

            soup = BeautifulSoup(res.text, 'html.parser')
            div = soup.find('div', class_='case_name')
            # 校验是否请求正确
            if div.label.text != d['name']:
                continue
            res = self._crawler.get(div.a['href'])
            if not res:
                continue
            soup = BeautifulSoup(res.text, 'html.parser')
            a_tags = soup.find('div', class_='bd clearfix').find_all('a')

            for a in a_tags:
                if a.text in exclude_keys:
                    continue
                if 'class' in a.attrs:
                    d[a.text] = 'notdata'
                    continue

                res = self._crawler.get(self.__domain + a['href'])
                if not res:
                    d[a.text] = a['href']

                html[a.text] = res.text

                soup = BeautifulSoup(res.text, 'html.parser')

                if a.text == '名称与编码':
                    for li in soup.find('div', class_='nameCoding').find_all('li'):
                        data[li.span.text] = li.p.text
                    continue
                elif a.text == '问诊与查体':
                    t1 = {}
                    for div in soup.find('div', class_='med_his_symp knw_box clearfix').find_all('div',
                                                                                                 class_='factor'):
                        h4 = div.find('h4')
                        t = []
                        for li in div.find_all('li'):
                            t.append({'name': li['kyinnername'], 'content': li.p.text})
                        t1[h4.text] = t
                    data[a.text] = t1
                    continue
                elif a.text == '治疗细则':
                    t = []
                    for a1 in soup.find('div', class_='dis_link').find_all('a'):
                        url = self.__domain + a1['href']
                        t_json = {
                            'url': url,
                            'name': a1['title']
                        }
                        res1 = self._crawler.get(url)
                        if not res1:
                            continue
                        soup1 = BeautifulSoup(res1.text, 'html.parser')
                        t_json['content'] = soup1.find('div', class_='editor_mirror editor_mirror_del').text
                        t.append(t_json)
                    data[a.text] = t
                    continue
                elif a.text == '诊疗指南':
                    data[a.text] = {}
                    for div in soup.find_all('div', class_='brow'):
                        t_zlzn = []
                        for div2 in div.find_all('div', class_='brow_content'):
                            t_zlzn.append({
                                'name': div2.a['title'],
                                'url': div2.a['href'],
                                'org': div2.p.text
                            })
                        data[a.text][div.h4.text] = t_zlzn
                    continue

                content = soup.find('div', class_='editor_mirror editor_mirror_del')

                if content is None:
                    continue
                data[a.text] = content.text

            self._html_cursor.insert_one(html)
            self._data_cursor.insert_one(data)
            self._urlpool.update_success_url({'url':data['url']})

    def parser(self):
        pass
