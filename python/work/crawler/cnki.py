#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import re
import time
import traceback

from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils.common import reg, remove_blank
from python.no_work.utils.excel import WriteXLSXCustom


def zgzw_recur_dic(_result, _code, _p):
    """
    数据存储，查找每个节点，看当前传入节点更像那个节点，然后转入节点下面进行查询。
    例如：12701 >> 1270101 >> 127010101
    _code在result那个节点下面
    :param _result:
    :param _code: 比对编码
    :param _p: 需要插入节点的参数
    :return: False返回上一层继续执行；True直接返回，说明找到。
    """
    if type(_result['child']) is not dict:
        return False

    # 优先匹配当前层级
    for _key, _value in _result['child'].items():
        if _code.startswith(_key):
            if zgzw_recur_dic(_value, _code, _p):
                return True
            _temp = _result['child'][_key]
            _p['child'] = {}
            _temp['child'][_code] = _p
            return True

    return False


def zgzw_recur_row(dic, s, arr=None):
    if arr is None:
        arr = []
    for key, value in dic.items():
        if value['child']:
            zgzw_recur_row(value['child'], s + value['name'] + '#', arr)

        arr.append(s + value['name'] + '#')


class cnki_zyfj(BaseCrawler):
    """
    中国知网，中药方剂信息爬取
    方剂目录地址：http://kb.tcm.cnki.net/TCM/TCM/Guide?node=12719&dbcode=zyff
            http://kb.tcm.cnki.net/TCM/TCM/GuideMore?node=12719&dbcode=zyff&kind=
        参数：node={node}
    方剂详细列表地址：http://kb.tcm.cnki.net/TCM/TCM/NaviItem?code=127010101&wd=%25E5%25B0%258F%25E9%259D%2592%25E9%25BE%2599%25E6%25B1%25A4&stype=&pageNum=1&pageSize=1000&dbcode=zyff&navikind=
        参数：code={code}, wd={wd};code为编码，wd为方剂名称
    """

    def __init__(self, ip='127.0.0.1'):
        super().__init__()

    def init_url(self):
        """
        初始化urlpool
        :return:
        """
        # 12701~12719
        url = 'http://kb.tcm.cnki.net/TCM/TCM/Guide?node={node}&dbcode=zyff'
        url2 = 'http://kb.tcm.cnki.net/TCM/TCM/GuideMore?node={node}&dbcode=zyff&kind='
        # 存储url到资源池中
        for i in range(1, 20):
            self._urlpool.save_url(params={
                'url': url.format(node=12700 + i),
                'url2': url2.format(node=12700 + i),
                'type': '1'
            })

    def startup(self, d):

        url = 'http://kb.tcm.cnki.net/TCM/TCM/NaviItem?code={code}&wd={wd}&stype=&pageNum=1&pageSize=1000&dbcode=zyff&navikind='

        while not self._urlpool.empty():
            # 参数获取
            _params = self._urlpool.get()

            if 'url2' not in _params:
                self._urlpool.put(_params)
                break

            _url = _params['url']
            url2 = _params['url2']

            # 请求获取数据
            # html = self.crawler.driver_get_url(_url, check_rule=self.check_rule)
            html1 = self._crawler.request_get_url(_url).decode('utf-8')
            html2 = self._crawler.request_get_url(url2).decode('utf-8')

            # 校验请求是否有效，无效更新链接地址
            if not (html1 and html2):
                self._urlpool.update({
                    'url': _params['url']
                }, {
                    '$set': {
                        'isenable': '1'
                    }
                })
                continue

            # 拼接请求结果，特殊化处理，该网站能容分两个请求得到
            s1 = '<div id="moreContent" class="moreIntro">'
            point = html1.index(s1) + len(s1)
            html = html1[0:point] + html2 + html1[point:]

            # 解析
            soup = BeautifulSoup(html, 'html.parser')
            a_tags = soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))

            # 获取新的地址进行存储
            for a in a_tags:
                _params = {
                    'url': url.format(code=reg(pattern='[0-9]+', s=a['href']), wd=a.text),
                    'type': '2'
                }
                self._urlpool.put(_params)

            # 存储HTML
            self.save_html(html, _params)

            self._urlpool.update_success_url(_params['url'])

        self.log.info('第二阶段开始......')
        while not self._urlpool.empty():
            # 参数获取
            _params = self._urlpool.get()
            _url = _params['url']

            # 请求获取数据
            html = self._crawler.request_get_url(_url).decode('utf-8')

            # 存储数据
            self.save_html(html, _params)
            self._urlpool.update_success_url(_params['url'])

    def parser_1(self):
        """
        解析数据，得到方剂类别树
        字典形式
        :return:
        """
        zyfz_zw_html_result = self._html_cursor.find({
            'url': {
                '$regex': '127[0-9]{2}&'
            }
        })

        result = {'child': {}, 'name': '父亲节点'}
        for r in zyfz_zw_html_result:
            html = r['html']
            url = r['url']
            soup = BeautifulSoup(html, 'html.parser')
            li_tag = soup.find('li', node=reg(pattern='127[0-9]{2}', s=url))

            params = {'name': li_tag.a.text, 'child': {}}
            result['child'][li_tag['node']] = params

            # 塞入第二大类
            for tag in li_tag.find_all('li'):
                params = {'name': tag.a.text}
                zgzw_recur_dic(result, tag['value'], params)

            a_tags = soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))

            for tag in a_tags:
                _code = reg(pattern='[0-9]{7,9}', s=tag['href'])
                params = {'name': tag.text}
                zgzw_recur_dic(result, _code, params)
        return result

    def parser_2(self):
        """
        将字典树拼转换为行形式
        :return:
        """
        dic = self.parser_1()
        arr = []
        zgzw_recur_row(dic=dic['child'], s='', arr=arr)
        print(arr)
        return arr

    @staticmethod
    def check_rule(html):
        """
        校验规则校验成功才算请求成
        :param html: 校验规则
        :return:
        """
        tag_a = []
        # 可能需要等待所以要进行请求
        time.sleep(0.5)
        _soup = BeautifulSoup(html, 'html.parser')
        tag_a += _soup.find_all('a', href=re.compile('navi\?node=[0-9]{7,9}'))

        flag = True
        if len(tag_a) > 0 or len(_soup.find_all('a', text='>> 详情信息')) > 0 \
                or len(_soup.find_all('a')) == 0:
            flag = False

        return flag


class disease_lczl(BaseCrawler):
    """
        名称：中国知网_临床诊疗_疾病
        URL：http://lczl.cnki.net/jb/index
        状态：完成
    """

    def _get_name(self):
        return 'cnki_disease_lczl'

    def _get_cn_name(self):
        return '中国知网_临床诊疗知识库_疾病'

    def _init_url(self):
        self._urlpool.save_url({
            'url': 'http://lczl.cnki.net/jb/index',
            'type': self._cn_name,
            'tree': 0
        })

    def startup(self, d):
        urls = []
        res = self._crawler.get(d['url'])
        if not res:
            return
        soup = self.to_soup(res.text)
        if d['tree'] == 0:
            # 首页->类别
            getpage_url = 'http://lczl.cnki.net/jb/getpage?page=0&type=类别路径&query={code}&mquery=&isfzzljb='
            search_url = 'http://lczl.cnki.net/jb/search?type=类别路径&query={code}&mquery=&issearch=0&isfzzljb='
            for li in soup.find_all('li', class_='fir_list'):
                urls.append({
                    'url': getpage_url.format(code=li['code']),
                    'search_url': search_url.format(code=li['code'], type='search'),
                    'name': li.a.text,
                    'type': self._cn_name,
                    'tree': 1
                })
        elif d['tree'] == 1:
            # 类别->疾病列表
            url = 'http://lczl.cnki.net/jbdetail/getdata?code={code}'
            for i in res.json()['list']:
                urls.append({
                    'url': url.format(code=i['code']),
                    'name': i['name'],
                    'code': i['code'],
                    'type': self._cn_name,
                    'tree': 2
                })

            # 类别->疾病列表->翻页。
            if 'search_url' in d:
                res1 = self._crawler.get(d['search_url'])

                d.pop('_id')
                d.pop('search_url')
                for i in range(2, int(res1.json()['total']) // 10 + 2):
                    d1 = {}
                    d1.update(d)
                    d1['url'] = d['url'].replace('page=0', 'page=' + str(i))
                    urls.append(d1)
        elif d['tree'] == 2:
            # 类别->疾病列表->翻页->疾病详细信息
            d.update(res.json()['jb'])
            self._data_cursor.insert_one(d)

        self.save_html(res.text, d)
        if urls:
            self._urlpool.save_url(urls)

    def parser(self):
        pass

    def to_excel(self):
        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())
        title = {
            '疾病编码': 'code',
            '疾病名称': 'name',
            '疾病中文名': 'jbzwm',
            '疾病别名': 'jbbm',
            '疾病英文名': 'jbywm',
            '疾病类别': 'jblb',
            '类别编码': 'lblj',
            'ICD': 'icd',
            '概述': 'gs',
            '病因': 'by',
            '药品列表': 'yplist',
            '临床表现': 'lcbx',
            '实验室检查': 'sysjc',
            '其它辅助检查': 'fzjc',
            '诊断': 'zd',
            '鉴别诊断': 'jbzd',
            '治疗': 'zl',
            '预后': 'yh',
            '并发症': 'bfz',
            '流行病学': 'lxbx',
            '发病机制': 'fbjz',
            '预防': 'yf',
            '文件编码': 'filename',
            'vsm': 'vsm',
            'ztCode': 'ztCode',
            '来源': 'type',
            'URL': 'url',
        }

        rowindex = 0
        write.write(rowindex=rowindex, data=list(title.keys()))

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k, v in title.items():
                if v in d:
                    content = str(d[v])
                    if content.startswith('<DIV>'):
                        soup = BeautifulSoup(content, 'html.parser')
                        row.append(remove_blank(soup.text))
                    else:
                        row.append(remove_blank(content))

            write.write(rowindex, row)
        write.close()


class disease_pmmp(BaseCrawler):
    """
        名称：中国知网_医学知识库_疾病
        URL：http://pmmp.cnki.net/Disease/Details.aspx?id=1
        状态：完成
    """

    def _get_name(self):
        """
        cnki_disease_pmmp
        :return:
        """
        return '中国知网_医学知识库_疾病'

    def _get_cn_name(self):
        return '中国知网_医学知识库_疾病'

    def _init_url(self):
        result = []
        for i in range(1, 7001):
            result.append({
                'url': 'http://pmmp.cnki.net/Disease/Details.aspx?id={id}'.format(id=i),
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self, d):
        res = self._crawler.get(d['url'])
        if res:
            self.save_html(res.text, d)
        else:
            self._urlpool.update({
                'url': d['url']
            }, {
                '$set': {
                    'isenable': '2'
                }
            })

    def parser(self):
        for d in self._html_cursor.find({'parser_enable': {'$exists': False}}):
            try:
                soup = self.to_soup(d['html'])
                trs = soup.find_all('tr')
                p = {
                    'url': d['url']
                }
                i = -1
                while True:
                    i += 1
                    tds = trs[i].find_all('td')
                    if len(tds) == 2:
                        p[tds[0].text] = tds[1].text
                    elif len(tds) == 1:
                        i += 1
                        if i >= len(trs):
                            break
                        p[tds[0].text] = trs[i].find('td').text
                self._data_cursor.insert_one(p)
                self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
            except BaseException as e:
                self.log.info(self._urlpool.update({'url': d['url']}, {'$set': {'isenable': '1'}}))
                self.log.info(self._html_cursor.delete_one({'url': d['url']}))
                self.log.error(d)
                self.log.error(traceback.format_exc())
                raise BaseException(e)

    def to_excel(self):
        title = ['【 疾病名称 】', '【 英文名称 】', '【 别　　名 】',  '【 缩　　写 】', '【 类　　别 】', '【 ICD    号 】', '【 概　　述 】', '【 流行病学 】', '【 病因 】', '【 发病机制 】', '【 临床表现 】', '【 并发症 】', '【 实验室检查 】', '【 其他辅助检查 】', '【 诊断 】', '【 鉴别诊断 】', '【 治疗 】', '【 预后 】', '【 预防 】', 'url',]

        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())

        rowindex = 0
        write.write(rowindex, title)

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k in title:
                if k in d:
                    row.append(remove_blank(d[k]))
                else:
                    row.append('')
            write.write(rowindex, row)

        write.close()


class operation_pmmp(BaseCrawler):
    """
        名称：中国知网_医学知识库_手术
        URL：http://pmmp.cnki.net/Operation/Details.aspx?id=810
        状态：完成
    """

    def _get_name(self):
        return '中国知网_医学知识库_手术'

    def _get_cn_name(self):
        return '中国知网_医学知识库_手术'

    def _init_url(self):
        result = []
        for i in range(1, 3501):
            result.append({
                'url': 'http://pmmp.cnki.net/Operation/Details.aspx?id={id}'.format(id=i),
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self, d):
        res = self._crawler.get(d['url'])
        if res:
            self.save_html(res.text, d)
        else:
            self._urlpool.update({
                'url': d['url']
            }, {
                '$set': {
                    'isenable': '2'
                }
            })

    def parser(self):
        for d in self._html_cursor.find({'parser_enable': {'$exists': False}}):
            try:
                soup = self.to_soup(d['html'])
                trs = soup.find_all('tr')
                p = {
                    'url': d['url']
                }
                i = -1
                while True:
                    i += 1
                    tds = trs[i].find_all('td')
                    if len(tds) == 2:
                        p[tds[0].text] = tds[1].text
                    elif len(tds) == 1:
                        i += 1
                        if i >= len(trs):
                            break
                        p[tds[0].text] = trs[i].find('td').text
                self._data_cursor.insert_one(p)
                self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
            except BaseException as e:
                self.log.info(self._urlpool.update({'url': d['url']}, {'$set': {'isenable': '1'}}))
                self.log.info(self._html_cursor.delete_one({'url': d['url']}))
                self.log.error(d)
                self.log.error(traceback.format_exc())
                # raise BaseException(e)

    def to_excel(self):
        title = ['【 手术名称 】', '【 别名 】', '【 英文名 】', '【 分类 】', '【  ICD编码 】', '【  概述 】',
                 '【  相关解剖 】', '【  适应症 】', '【  禁忌症 】', '【  术前准备 】', '【  麻醉和体位 】',
                 '【  手术步骤  】', '【  术中注意要点 】', '【  术后处理 】', '【  述评 】', 'url', ]

        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())

        rowindex = 0
        write.write(rowindex, title)

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k in title:
                if k in d:
                    row.append(remove_blank(d[k]))
                else:
                    row.append('')
            write.write(rowindex, row)

        write.close()


class operation_lczl(BaseCrawler):
    """
        名称：中国知网_临床诊疗知识库_操作规范
        URL：http://lczl.cnki.net/jb/index
        状态：完成
    """

    def _get_name(self):
        return '中国知网_临床诊疗知识库_操作规范'

    def _get_cn_name(self):
        return '中国知网_临床诊疗知识库_操作规范'

    def _init_url(self):
        self._urlpool.save_url({
            'url': 'http://lczl.cnki.net/gf/index',
            'type': self._cn_name,
            'tree': 0
        })

    def startup(self, d):
        urls = []
        res = self._crawler.get(d['url'])
        if not res:
            return
        soup = self.to_soup(res.text)
        if d['tree'] == 0:
            # 首页->类别
            getpage_url = 'http://lczl.cnki.net/gf/getpage?page=0&type=类别路径&query={code}&mquery='
            search_url = 'http://lczl.cnki.net/gf/search?type=类别路径&query={code}&mquery='
            for li in soup.find_all('li', class_='fir_list'):
                urls.append({
                    'url': getpage_url.format(code=li['code']),
                    'search_url': search_url.format(code=li['code'], type='search'),
                    'name': li.a.text,
                    'type': self._cn_name,
                    'tree': 1
                })
        elif d['tree'] == 1:
            # 类别->疾病列表
            url = 'http://lczl.cnki.net/gfdetail/getdata?code={code}'
            for i in res.json()['list']:
                urls.append({
                    'url': url.format(code=i['code']),
                    'name': i['name'],
                    'code': i['code'],
                    'type': self._cn_name,
                    'tree': 2
                })

            # 类别->疾病列表->翻页。
            if 'search_url' in d:
                res1 = self._crawler.get(d['search_url'])

                d.pop('_id')
                d.pop('search_url')
                for i in range(2, int(res1.json()['total']) // 10 + 2):
                    d1 = {}
                    d1.update(d)
                    d1['url'] = d['url'].replace('page=0', 'page=' + str(i))
                    urls.append(d1)
        elif d['tree'] == 2:
            # 类别->疾病列表->翻页->疾病详细信息
            d.update(res.json()['jb'])
            self._data_cursor.insert_one(d)

        self.save_html(res.text, d)
        if urls:
            self._urlpool.save_url(urls)

    def parser(self):
        pass

    def to_excel(self):
        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())
        title = {
            '名称': 'name',
            '别名': 'othername',
            '禁忌症': 'taboo',
            '准备': 'preparation',
            '操作规范编码': 'code',
            '适应症': 'adaptation',
            '方法': 'method',
            '结果判断': 'result',
            '注意事项': 'notice',
            '分类名称': 'routename',
            '分类代码': 'route',
            'vsm': 'vsm',
            '来源': 'type',
            'URL': 'url',
        }

        rowindex = 0
        write.write(rowindex=rowindex, data=list(title.keys()))

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k, v in title.items():
                if v in d:
                    content = str(d[v])
                    if content.startswith('<DIV>'):
                        soup = BeautifulSoup(content, 'html.parser')
                        row.append(remove_blank(soup.text))
                    else:
                        row.append(remove_blank(content))

            write.write(rowindex, row)
        write.close()


class diagnostic_examination(BaseCrawler):
    """
        名称：中国知网_医学知识库_辅助检查库
        URL：http://pmmp.cnki.net/DiagnosticExamination/Details.aspx?id=1
        状态：完成
    """

    def _get_name(self):
        return '中国知网_医学知识库_辅助检查库'

    def _get_cn_name(self):
        return '中国知网_医学知识库_辅助检查库'

    def _init_url(self):
        result = []
        for i in range(1, 1160):
            result.append({
                'url': 'http://pmmp.cnki.net/DiagnosticExamination/Details.aspx?id={id}'.format(id=i),
                'type': self._cn_name,
                'tree': 0
            })
        self._urlpool.save_url(result)

    def startup(self, d):
        res = self._crawler.get(d['url'])
        if res:
            self.save_html(res.text, d)
        else:
            self._urlpool.update({
                'url': d['url']
            }, {
                '$set': {
                    'isenable': '2'
                }
            })

    def parser(self):
        for d in self._html_cursor.find({'parser_enable': {'$exists': False}}):
            try:
                soup = self.to_soup(d['html'])
                trs = soup.find_all('tr')
                p = {
                    'url': d['url']
                }
                i = -1
                while True:
                    i += 1
                    tds = trs[i].find_all('td')
                    if len(tds) == 2:
                        p[tds[0].text] = tds[1].text
                    elif len(tds) == 1:
                        i += 1
                        if i >= len(trs):
                            break
                        p[tds[0].text] = trs[i].find('td').text
                self._data_cursor.insert_one(p)
                self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
            except BaseException as e:
                self.log.info(self._urlpool.update({'url': d['url']}, {'$set': {'isenable': '1'}}))
                self.log.info(self._html_cursor.delete_one({'url': d['url']}))
                self.log.error(d)
                self.log.error(traceback.format_exc())
                # raise BaseException(e)

    def to_excel(self):
        title = ['【 检查名称 】', '【 分类 】', '【 英文名 】', '【 别名 】', '【 概述 】', '【临床意义】', '【 原理 】',
                 '【正常值】', '【 试剂】', '【操作方法】', '【附注】', 'url', ]

        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())

        rowindex = 0
        write.write(rowindex, title)

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k in title:
                if k in d:
                    row.append(remove_blank(d[k]))
                else:
                    row.append('')
            write.write(rowindex, row)

        write.close()


class auxiliary_examination_lczl(BaseCrawler):
    """
        名称：中国知网_诊疗知识库_辅助检查
        URL：http://lczl.cnki.net/jc/index
        状态：完成
    """

    def _get_cn_name(self):
        return '中国知网_临床诊疗知识库_辅助检查'

    def _get_name(self):
        return '中国知网_临床诊疗知识库_辅助检查'

    def _init_url(self):
        self._urlpool.save_url({
            'url': 'http://lczl.cnki.net/jc/index',
            'type': self._cn_name,
            'tree': 0
        })

    def startup(self, d):
        urls = []
        res = self._crawler.get(d['url'])
        if not res:
            return
        soup = self.to_soup(res.text)
        if d['tree'] == 0:
            # 首页->类别
            getpage_url = 'http://lczl.cnki.net/jc/getpage?page=0&type=类别路径&query={code}&mquery='
            search_url = 'http://lczl.cnki.net/jc/search?type=类别路径&query={code}&mquery='
            for li in soup.find_all('li', class_='fir_list'):
                urls.append({
                    'url': getpage_url.format(code=li['code']),
                    'search_url': search_url.format(code=li['code'], type='search'),
                    'name': li.a.text,
                    'type': self._cn_name,
                    'tree': 1
                })
        elif d['tree'] == 1:
            # 类别->疾病列表
            url = 'http://lczl.cnki.net/jcdetail/getdata?code={code}'
            for i in res.json()['list']:
                urls.append({
                    'url': url.format(code=i['filename']),
                    'name': i['cname'],
                    'code': i['filename'],
                    'type': self._cn_name,
                    'tree': 2
                })

            # 类别->检查列表->翻页。
            if 'search_url' in d:
                res1 = self._crawler.get(d['search_url'])

                d.pop('_id')
                d.pop('search_url')
                for i in range(2, int(res1.json()['total']) // 10 + 2):
                    d1 = {}
                    d1.update(d)
                    d1['url'] = d['url'].replace('page=0', 'page=' + str(i))
                    urls.append(d1)
        elif d['tree'] == 2:
            # 类别->检查列表->翻页->检查详细信息
            d.update(res.json()['jb'])
            self._data_cursor.insert_one(d)

        self.save_html(res.text, d)
        if urls:
            self._urlpool.save_url(urls)

    def parser(self):
        pass

    def to_excel(self):
        write = WriteXLSXCustom('.\\cnki\\' + self._get_cn_name())
        title = {
            '中文名称': 'name',
            '英文名称': 'ename',
            '类别代码': 'route',
            '检查代码': 'code',
            '正常值': 'common',
            '试剂': 'agentia',
            '概述': 'overview',
            '原理': 'principle',
            '临床意义': 'meaning',
            '操作方法': 'operation',
            '附注': 'tips',
            '其它': 'othername',
            'vsm': 'vsm',
            'URL': 'url',
            '来源': 'type',
        }

        rowindex = 0
        write.write(rowindex=rowindex, data=list(title.keys()))

        for d in self._data_cursor.find():
            rowindex += 1
            row = []
            for k, v in title.items():
                if v in d:
                    content = str(d[v])
                    if content.startswith('<DIV>'):
                        soup = BeautifulSoup(content, 'html.parser')
                        row.append(remove_blank(soup.text))
                    else:
                        row.append(remove_blank(content))

            write.write(rowindex, row)
        write.close()
