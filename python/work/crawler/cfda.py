#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import datetime
import time
import re
import random

from bs4 import BeautifulSoup

from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils.common import reg
from python.no_work.utils.oracle import OralceCursor

insert_sql = """
INSERT INTO KBMS_DFSX_KNOWLEDGE_UP (ID, PRODUCT_NAME, TRAD_NAME, SPEC, PERMIT_NO,
                                    PRODUCTION_UNIT, CLINICAL_STATE, TYPE, IS_ENABLE, IS_SUBMIT)
SELECT *
FROM (
  SELECT
    T2.ID                                                                                                ID,
    DECODE(T1.PRODUCT_NAME, '', ('_' || T2.PRODUCT_NAME), T2.PRODUCT_NAME, ('_' || T2.PRODUCT_NAME), NULL, ('_' || T2.PRODUCT_NAME),
           ('#_' || T1.PRODUCT_NAME))                                                                    PRODUCT_NAME,
--       T1.PRODUCT_NAME CFDA产品名称, T2.PRODUCT_NAME 药品列表产品名称,
    DECODE(T1.TRAD_NAME, '', ('_' || T2.TRAD_NAME), T2.TRAD_NAME, ('_' || T2.TRAD_NAME), NULL, ('_' || T2.TRAD_NAME),
           ('#_' || T1.TRAD_NAME))                                                                       TRAD_NAME,
--       T1.TRAD_NAME CFDA商品名称, T2.TRAD_NAME 药品列表商品名称,
    DECODE(T1.SPEC, '', ('_' || T2.SPEC), T2.SPEC, ('_' || T2.SPEC), NULL, ('_' || T2.SPEC), ('#_' || T1.SPEC))                SPEC,
--       T1.SPEC CFDA规格, T2.SPEC 药品列表规格,
    DECODE(T1.PERMIT_NO, '', ('_' || T2.PERMIT_NO), T2.PERMIT_NO, ('_' || T2.PERMIT_NO), NULL, ('_' || T2.PERMIT_NO),
           ('#_' || T1.PERMIT_NO))                                                                       PERMIT_NO,
--       T1.PERMIT_NO CFDA批准文号, T2.PERMIT_NO 药品列表批准文号,
    DECODE(T1.PRODUCTION_UNIT, '', ('_' || T2.PRODUCTION_UNIT), T2.PRODUCTION_UNIT, ('_' || T2.PRODUCTION_UNIT), NULL,
           ('_' || T2.PRODUCTION_UNIT), ('#_' ||
                                         T1.PRODUCTION_UNIT))                                            PRODUCTION_UNIT,
--       T1.PRODUCTION_UNIT CFDA生产单位, T2.PRODUCTION_UNIT 药品列表生产单位,
    CASE WHEN T2.CLINICAL_STATE = '注销' AND T1.ID IS NOT NULL
      THEN '#_正常'
    WHEN T1.ID IS NOT NULL
      THEN '_正常'
    ELSE '_注销' END                                                                                       CLINICAL_STATE,
    '1'                                                                                                  TYPE,
    '1'                                                                                                  IS_ENABLE,
    '0'
      IS_SUBMIT
  FROM KBMS_DFSX_KNOWLEDGE_UP_BAK T1
    RIGHT JOIN KBMS_DRUG_FROM_SX T2 ON T1.ID = T2.ID
  WHERE TYPE = '1')
WHERE PRODUCT_NAME LIKE '#%'
      OR TRAD_NAME LIKE '#%'
      OR SPEC LIKE '#%'
      OR PERMIT_NO LIKE '#%'
      OR PRODUCTION_UNIT LIKE '#%'
      OR CLINICAL_STATE LIKE '#%'

"""
update_sql = """
UPDATE KBMS_DFSX_KNOWLEDGE_UP SET IS_ENABLE = '5' WHERE IS_ENABLE = '1'
"""

ZC_EX = ['气体', '医用氧(气态分装)', '医用氧', '医用氧(气态)', '化学药品', '医用气体', '医用气体(气态氧)',
         '其他', '气态', '液态和气态', '非剂型', '气态 液态', '体外诊断试剂', '鼻用制剂', '液态气体',
         '非制剂,其他:氧', '液态', '氧(气态、液态)', '液体	', '气剂', '液态氧', '气体、液态',
         '医用氧(液态)', '有效成份', '液态空气', '吸入性气体', '氧', '医用氧气', '氧气', '医用氧(气态、液态)',
         '呼吸', '其他:医用氧(气态)', '有效部位', '制剂中间体', '放免药盒', '药用辅料', '原料', '辅料',
         '特殊药用辅料', '颗粒剂(制剂中间体)', '制剂中间体水包衣颗粒', '制剂用中间体', '特殊辅料', '放射性密封源',
         '制剂:密封源', '放射性密封籽源', '药用辅料(供注射用)', '药用特殊辅料', '非制剂:辅料', '原料呀', '新辅料'
         ]
PRODUCT_NAME_EX = ['氧', '氧(液态)', '氧(气态)', '医用液态氧', '医用氧气', '医用氧(液态)']

RE_COMPILE = re.compile('869[0-9]{11}')


class cfda(BaseCrawler):
    """
    国家食品药品监督管理总局
    2018-3-27
        1.请求错误的url进行标记，因为发现有部分数据请求为空

    需要提交
    """

    def __init__(self, ip='127.0.0.1'):
        self.__domain_url = 'http://app1.sfda.gov.cn/datasearch/face3/'
        self.__href_re = 'javascript:commitForECMA[\u4e00-\u9fa50-9a-zA-Z\(\)\?&=,\'.]+'

        self.oralce_cursor = OralceCursor()
        super().__init__(ip)

    def _get_cn_name(self):
        return 'CFDA'

    def _get_name(self):
        return 'cfda'

    def _init_url(self):
        """
        http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}
        code:25代表国产药品，36代表进口药品
        page:翻页参数
        :return:
        """
        url = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}'
        result = []
        p = {
            '国产': {
                'code': 25,
                'page': 11061
            },
            '进口': {
                'code': 36,
                'page': 274
            }
        }
        for k, v in p.items():
            for i in range(1, v['page'] + 1):
                p1 = {
                    'url': url.format(code=v['code'], page=i),
                    'type': 'CFDA-国产药',
                    'tree': 0
                }
                result.append(p1)
        self._urlpool.save_url(result)

    def startup(self, params):
        d1 = datetime.datetime.now()
        html = self._crawler.driver_get_url(params['url'])
        soup = BeautifulSoup(html, 'html.parser')
        if params['tree'] == 0:
            a_tags = soup.find_all('a', href=re.compile(self.__href_re))

            if a_tags and len(a_tags):

                url_list = []
                # 更新链接请求成功
                for a in a_tags:
                    url_list.append({
                        'type': params['type'],
                        'url': self.__domain_url + reg(
                            'content.jsp\?tableId=[0-9]+&tableName=TABLE[0-9]+&tableView=[\u4e00-\u9fa50]+&Id=[0-9]+',
                            a['href']),
                        'text': a.text,
                        'tree': 1
                    })
                self._urlpool.save_url(url_list)
        elif params['tree'] == 1:
            tbody = soup.find_all('tbody')
            if tbody:
                pass
            else:
                time.sleep(random.randint(100, 500))
                return

        self.save_html(html, params)

        d2 = datetime.datetime.now()
        date = (d2 - d1).total_seconds()
        # 说明响应变慢了，等等，给服务器减压。
        # 存在请求小于0.1秒的情况，这些都是有数据，只是返回不正常
        if date > 10 or date < 0.3:
            time.sleep(random.randint(100, 500))

    def parser(self):
        self.log.info('开始')
        query = {'tree': 1, 'parser_enable': {'$exists': False}}
        for i, d in enumerate(self._html_cursor.find(query, no_cursor_timeout=True)):
            if (i + 1) % 10000 == 0:
                self.log.info(i)

            soup = BeautifulSoup(d['html'], 'html.parser')
            tr_tags = soup.find_all('tr')[1:-3]
            row = {
                '_id': d['_id'],
                'url': d['url'],
                'text': d['text']
            }
            for tr in tr_tags:
                text = tr.text.split('\n')
                if len(text) < 3:
                    continue
                row[text[1]] = text[2]

            text_b = []
            row_b = []

            if '药品本位码' in row:
                text_b = RE_COMPILE.findall(d['text'])
                row_b = RE_COMPILE.findall(row['药品本位码'])
                text_b.sort()
                row_b.sort()

            # 数据有效加入，数据无效进行更新
            if ''.join(row_b).__contains__(''.join(text_b)):
                self._data_cursor.insert(row)
                self._html_cursor.update_one({'url': d['url']}, {'$set': {'parser_enable': '成功'}})
            else:
                self._urlpool.update({'url': d['url']}, {'$set': {'isenable': '1'}})
                self._html_cursor.delete_one({'url': d['url']})

    def parser2(self):
        """
        比较原始数据列表上的本位码，是不是跟解析后的本位码一样
        1. 按照URL查取data，url中查找对应的数据
        2. 进行比较
        3. 不相同，那么删除html，更新url.isenable == 1
        :return:
        """
        index = 0
        for data in self._data_cursor().find():
            index += 1
            if index < 0:
                continue
            if index % 1000 == 0:
                print(index)
            if 'text' not in data:
                continue

            if ('药品本位码' not in data) or \
                    (data and not str(data['text']).__contains__(data['药品本位码'])):
                self._urlpool.update({'_id': data['_id']}, {'isenable': '1'})
                self._html_cursor.delete_one({'url': data['url']})

    def to_oracle(self):
        """
        数据转移到oracle上
        :return:
        """
        self.log.info('数据库存储开始')
        self.oralce_cursor.executeSQL('DELETE KBMS_DFSX_KNOWLEDGE_UP_BAK')

        sql = 'INSERT INTO KBMS_DFSX_KNOWLEDGE_UP_BAK (ID, PRODUCT_NAME, TRAD_NAME, SPEC, ZC_FORM, PERMIT_NO, PRODUCTION_UNIT, CODE_REMARK, TYPE) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)'
        params = {
            'ID': ['药品本位码'],
            'PRODUCT_NAME': ['产品名称', '产品名称（中文）'],
            'TRAD_NAME': ['商品名', '商品名（中文）'],
            'SPEC': ['规格', '规格（中文）'],
            'ZC_FORM': ['剂型', '剂型（中文）'],
            'PERMIT_NO': ['批准文号', '注册证号'],
            'PRODUCTION_UNIT': ['生产单位', '生产厂商（英文）'],
            'CODE': ['药品本位码备注']
        }
        params1 = ['ID', 'PRODUCT_NAME', 'TRAD_NAME', 'SPEC', 'ZC_FORM', 'PERMIT_NO',
                   'PRODUCTION_UNIT', 'CODE']

        # 循环记录
        for data in self._data_cursor.find():
            row = ['0', '1', '2', '3', '4', '5', '6', '', '8']
            # 字典
            for i, k in enumerate(params1):
                # 字典中的数组
                for v in params[k]:
                    if v in data:
                        row[i] = data[v]

            # 剂型不在被收集队列里面；剂型不在排除队列里面；
            # 剂型不包含原料药，试剂这两个字样；剂型需要包含中文；
            # 剂型不为空；
            # 产品名称不在排除队列中；产品名称不包含试剂；
            if row[4] not in ZC_EX \
                    and not reg('(原料药)|(试剂)', row[4]) \
                    and reg('[\u4e00-\u9fa5]+', row[4]) \
                    and row[1] not in PRODUCT_NAME_EX \
                    and not reg('(试剂)', row[1]) \
                    and row[4]:
                """"""
                row[8] = '1'
            else:
                row[8] = '0'

            # 校验本位码农是否多个
            if len(row[0]) < 10:
                continue
            if row[7] != '':
                for code in row[7].split('；'):
                    row[0] = reg('[0-9]{14}', code)
                    row[3] = reg('\[.*\]', code).replace('[', '').replace(']', '')
                    self.oralce_cursor.executeSQLParams(sql, row)
            else:
                self.oralce_cursor.executeSQLParams(sql, row)

        # 更新数据
        self.oralce_cursor.executeSQL(update_sql)
        # 插入数据
        self.oralce_cursor.executeSQL(insert_sql)
        self.log.info('数据库存储结束')
