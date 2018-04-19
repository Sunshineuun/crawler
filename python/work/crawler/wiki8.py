#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 医学百科
import re

from bs4 import Tag

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils.common import remove_blank
from python.no_work.utils.excel import WriteXLSXCustom

DOMINA = 'https://www.wiki8.com'


class disease(BaseCrawler):
    """
        名称：医学百科_疾病百科
        URL：https://www.wiki8.com/Categorize/%E7%96%BE%E7%97%85.html
        状态：完成
    """

    def _get_name(self):
        return '医学百科_疾病百科'

    def _get_cn_name(self):
        return '医学百科_疾病百科'

    def _init_url(self):
        url = 'https://www.wiki8.com/Categorize/%E7%96%BE%E7%97%85_{page}.html'
        result = []
        for p in range(1, 20):
            result.append({
                'url': url.format(page=p),
                'type': self._cn_name,
                'tree': 0
            })
        res = self._crawler.get('https://www.wiki8.com/Categorize/%E7%96%BE%E7%97%85.html')
        soup = self.to_soup(res.text)
        for a in soup.find(id='treeRoot').find_all('a'):
            result.append({
                'url': DOMINA + a['href'],
                'name': a.text,
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self, d):
        res = self._crawler.get(d['url'])
        if not res:
            return

        soup = self.to_soup(res.text)

        # 不是列表的，是详细信息的，因为初始化列表中有些是疾病的详细信息，故此需要做出判断。
        if not soup.find('ul', class_='cateList'):
            d['tree'] = 1

        if d['tree'] == 0:
            a_tags = soup.find('ul', class_='cateList').find_all('a')
            result = []
            for a in a_tags:
                result.append({
                    'url': DOMINA + a['href'],
                    'name': a.text,
                    'type': self._cn_name,
                    'tree': 1
                })
            page = soup.find('ul', class_='page')
            if page:
                _a = re.findall('[0-9]+', page.li.text)
                if _a[1] == '1':
                    for i in range(2, int(_a[0]) + 1):
                        result.append({
                            'url': d['url'].replace('.html', '_' + str(i) + '.html'),
                            'type': self._cn_name,
                            'tree': 0
                        })
            self._urlpool.save_url(result)
        elif d['tree'] == 1:
            # 这里是否需要校验一下，请求的数据是否有效
            pass
        self.save_html(res.text, d)

    def parser(self):
        result = []
        for d in self._html_cursor.find({'tree': 1, 'parser_enable': {'$exists': False}}):
            soup = self.to_soup(d['html'])
            key = ''
            p = {
                'url': d['url'],
                'name': d['name'],
                'type': d['type'],
            }
            content = soup.find(id='content')
            if content is None:
                self.log.error(d['url'])
                continue
            for tag in content.contents:
                if type(tag) != Tag or tag.name == 'div':
                    continue

                if tag.name == 'h2':
                    key = re.sub('[·' + d['name'].replace('-', '\\-') + ']', '', tag.text)
                # elif tag.name == 'h3':
                #     key += tag.text
                elif tag.name in ['p', 'h4', 'h3']:
                    key = re.sub('[. 的0-9]', '', key)
                    if key not in p:
                        p[key] = ''
                    p[key] += tag.text
                    p[key] += '\n'
            result.append(p)
            self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
        self._data_cursor.insert_many(result)

    def to_excel(self):
        title = {
            'key': [],
            'regex': [],
            'url': [],
            '疾病名称': [],
            '英文名称': [],
            '别名': ['疾病别名'],
            'ICD号': ['ICD编码'],
            '临床分类': ['常见类型'],
            '概述': [],
            '疾病概述': [],
            '病因学': ['病因', '主要病因', '病因和发病机制', '疾病病因', '进入人体途径及影响程度因素', '危险因素'],
            '临床表现': ['症状体征', '传播途径', '症状'],
            '治疗措施': ['治疗方案', '治疗', '药物治疗', '治疗方法', '适应症', '禁忌症', '手术治疗', '治疗原则', '用药原则', '相关用药', '防治', '处理'],
            '诊断': ['诊断检查', '诊断及相关检查', '诊断要点', '诊断标准'],
            '流行病学': ['流行病学资料', '流行学'],
            '预防': ['预后及预防'],
            '并发症': ['并发症及后遗症'],
            '实验室检查': ['辅助检查', '相关检查', '其他辅助检查'],
            '鉴别诊断': ['需要与鉴别疾病', '需要与相鉴别疾病', '诊断依据', '诊断与鉴别诊断'],
            '病因病理病机': ['发病机制', '病理学特征', '病原学', '发病机理', '病理改变', '病理病机', '常见机制'],
        }
        write = WriteXLSXCustom('.\\wiki8\\' + self._get_cn_name())

        # 写入表头
        rowindex = 0
        write.write(rowindex=rowindex, data=list(title.keys()))

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k, v in title.items():
                col = ''
                for k1 in [k] + v:
                    if k1 in d:
                        col += k1 + ':' + remove_blank(d[k1]) + '\n'
                row.append(col)
            write.write(rowindex=rowindex, data=row)
        write.close()


class operation(BaseCrawler):
    def _get_name(self):
        return '医学百科_手术百科'

    def _get_cn_name(self):
        return '医学百科_手术百科'

    def _init_url(self):
        url = 'https://www.wiki8.com/Categorize/%E6%89%8B%E6%9C%AF_{page}.html'
        result = []
        for p in range(1, 109):
            result.append({
                'url': url.format(page=p),
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self, d):
        res = self._crawler.get(d['url'])
        if not res:
            return

        soup = self.to_soup(res.text)

        if d['tree'] == 0:
            a_tags = soup.find('ul', class_='cateList').find_all('a')
            result = []
            for a in a_tags:
                result.append({
                    'url': DOMINA + a['href'],
                    'page_url': d['url'],
                    'name': a.text,
                    'type': self._cn_name,
                    'tree': 1
                })
            self._urlpool.save_url(result)
        elif d['tree'] == 1:
            # 这里是否需要校验一下，请求的数据是否有效
            pass
        self.save_html(res.text, d)

    def parser(self):
        result = []
        for d in self._html_cursor.find({'tree': 1, 'parser_enable': {'$exists': False}}):
            soup = self.to_soup(d['html'])
            key = ''
            p = {
                'url': d['url'],
                'name': d['name'],
                'type': d['type'],
            }
            content = soup.find(id='content')
            if content is None:
                self.log.error(d['url'])
                continue
            for tag in content.contents:
                if type(tag) != Tag or tag.name == 'div':
                    continue

                if tag.name == 'h2':
                    key = re.sub('[·' + d['name'].replace('-', '\\-') + ']', '', tag.text)
                # elif tag.name == 'h3':
                #     key += tag.text
                elif tag.name in ['p', 'h4', 'h3']:
                    key = re.sub('[. 的0-9]', '', key)
                    if key not in p:
                        p[key] = ''
                    p[key] += tag.text
                    p[key] += '\n'
            result.append(p)
            self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
        self._data_cursor.insert_many(result)
