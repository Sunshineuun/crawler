#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie

import datetime
import re

from bs4 import BeautifulSoup

from minnie.crawler.common.Utils import reg
from python.no_work.crawler.base_crawler import BaseCrawler
from python.no_work.utils import mlogger
from python.no_work.utils.oracle import OralceCursor

logger = mlogger.get_defalut_logger('cfda.log', 'cfda')

insert_sql = """
SELECT *
FROM (
  SELECT
    T2.ID                                                                                                ID,
    DECODE(T1.PRODUCT_NAME, T2.PRODUCT_NAME, ('_' || T2.PRODUCT_NAME), NULL, ('_' || T2.PRODUCT_NAME),
           ('#_' || T1.PRODUCT_NAME))                                                                    PRODUCT_NAME,
      T1.PRODUCT_NAME CFDA产品名称, T2.PRODUCT_NAME 药品列表产品名称,
    DECODE(T1.TRAD_NAME, T2.TRAD_NAME, ('_' || T2.TRAD_NAME), NULL, ('_' || T2.TRAD_NAME),
           ('#_' || T1.TRAD_NAME))                                                                       TRAD_NAME,
      T1.TRAD_NAME CFDA商品名称, T2.TRAD_NAME 药品列表商品名称,
    DECODE(T1.SPEC, T2.SPEC, ('_' || T2.SPEC), NULL, ('_' || T2.SPEC), ('#_' || T1.SPEC))                SPEC,
      T1.SPEC CFDA规格, T2.SPEC 药品列表规格,
    DECODE(T1.ZC_FORM, T2.ZC_FORM, ('_' || T2.ZC_FORM), NULL, ('_' || T2.ZC_FORM), ('#_' || T1.ZC_FORM)) ZC_FORM,
      T1.ZC_FORM CFDA注册剂型, T2.ZC_FORM 药品列表注册剂型,
    DECODE(T1.PERMIT_NO, T2.PERMIT_NO, ('_' || T2.PERMIT_NO), NULL, ('_' || T2.PERMIT_NO),
           ('#_' || T1.PERMIT_NO))                                                                       PERMIT_NO,
      T1.PERMIT_NO CFDA批准文号, T2.PERMIT_NO 药品列表批准文号,
    DECODE(T1.PRODUCTION_UNIT, T2.PRODUCTION_UNIT, ('_' || T2.PRODUCTION_UNIT), NULL,
           ('_' || T2.PRODUCTION_UNIT), ('#_' ||
                                         T1.PRODUCTION_UNIT))                                            PRODUCTION_UNIT,
      T1.PRODUCTION_UNIT CFDA生产单位, T2.PRODUCTION_UNIT 药品列表生产单位,
    CASE WHEN T2.CLINICAL_STATE = '注销' AND T1.ID IS NOT NULL
      THEN '#_正常'
    WHEN T1.ID IS NOT NULL
      THEN '_正常'
    ELSE '_注销' END                                                                                       CLINICAL_STATE,
    '1'                                                                                                  TYPE,
    '1'                                                                                                  IS_ENABLE,
    '0'                                                                                                  IS_SUBMIT
  FROM KBMS_DFSX_KNOWLEDGE_UP_BAK T1
    RIGHT JOIN KBMS_DRUG_FROM_SX T2 ON T1.ID = T2.ID
  WHERE TYPE = '1')
WHERE PRODUCT_NAME LIKE '#%'
      OR TRAD_NAME LIKE '#%'
      OR SPEC LIKE '#%'
      OR ZC_FORM LIKE '#%'
      OR PERMIT_NO LIKE '#%'
      OR PRODUCTION_UNIT LIKE '#%'
      OR CLINICAL_STATE LIKE '#%'
"""

update_sql = """
UPDATE KBMS_DFSX_KNOWLEDGE_UP SET IS_ENABLE = '5' WHERE IS_ENABLE = '1'
"""


class cfda(BaseCrawler):
    """
    国家食品药品监督管理总局
    """
    # TODO
    """
        1.数据对比问题
    """

    def __init__(self, ip='127.0.0.1'):
        super().__init__(ip)
        self.pici = 0
        self.url_index = 0

        self.oralce_cursor = OralceCursor()

    def _get_cn_name(self):
        return 'CFDA'

    def _get_name(self):
        return 'cfda1'

    def _init_url(self):
        """
        http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}
        code:25代表国产药品，36代表进口药品
        page:翻页参数
        :return:
        """
        self.url_index = self._urlpool.find_all_count()
        if self.url_index:
            return

        # 国产药品
        url_template = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId={code}&curstart={page}'
        _params = {
            '国产': {
                'code': 25,
                'page': 11061
            },
            '进口': {
                'code': 36,
                'page': 274
            }
        }
        result_list = []
        for k, v in _params.items():
            for i in range(1, v['page'] + 1):
                _p = {
                    '_id': str(v['code']) + str(i),
                    'url': url_template.format(code=v['code'], page=i),
                    'type': 'CFDA-国产药'
                }
                result_list.append(_p)
        self._urlpool.save_url(result_list)
        self.url_index = self._urlpool.find_all_count()

    def get_cookie(self):
        cookie = ''
        for dic in self._crawler.get_driver().get_cookies():
            cookie += dic['name'] + '=' + dic['value'] + ';'
        return cookie

    def startup(self):
        # 域名前缀
        domain_url = 'http://app1.sfda.gov.cn/datasearch/face3/'
        href_re = 'javascript:commitForECMA[\u4e00-\u9fa50-9a-zA-Z\(\)\?&=,\'.]+'

        while not self._urlpool.empty():
            d1 = datetime.datetime.now()
            params = self._urlpool.get()
            # html_b = self.crawler.request_get_url(params['url'], header={'Cookie': self.get_cookie()})
            # html = html_b.decode('utf-8')
            html = self._crawler.driver_get_url(params['url'])
            soup = BeautifulSoup(html, 'html.parser')
            if params['url'].__contains__('search.jsp'):
                a_tags = soup.find_all('a', href=re.compile(href_re))

                # if not a_tags or len(a_tags) == 0:
                #     html = self.crawler.driver_get_url(params['url'])

                # soup = BeautifulSoup(html)
                # a_tags = soup.find_all('a', href=re.compile(href_re))

                if a_tags and len(a_tags):
                    params['html'] = html
                    self._html_cursor.insert(params)
                    self._urlpool.update_success_url(params['url'])
                    params.pop('html')

                    url_list = []
                    # 更新链接请求成功
                    for a in a_tags:
                        _p = {
                            '_id': self.url_index,
                            'type': params['type'],
                            'url': domain_url + reg(
                                'content.jsp\?tableId=[0-9]+&tableName=TABLE[0-9]+&tableView=[\u4e00-\u9fa50]+&Id=[0-9]+',
                                a['href']),
                            'text': a.text
                        }
                        self.url_index += 1
                        url_list.append(_p)
                    self._urlpool.save_url(url_list)
            elif params['url'].__contains__('content.jsp'):
                tbody = soup.find_all('tbody')
                # if tbody:
                #     html = self.crawler.driver_get_url(params['url'])
                #
                # soup = BeautifulSoup(html)
                # tbody = soup.find_all('tbody')
                if tbody:
                    params['html'] = html
                    # 保存html数据
                    self._html_cursor.insert(params)
                    # 更新数据
                    self._urlpool.update_success_url(params['url'])
            else:
                logger.error('异常情况：' + params['url'])

            d2 = datetime.datetime.now()
            logger.info('耗时：' + str((d2 - d1).total_seconds()))

    def parser(self):
        logger.info('开始')
        query = {'url': {'$regex': 'http:[a-z0-9/.]+content.jsp\?'}}
        rows = []
        for i, data in enumerate(self._html_cursor.find(query)):
            if (i + 1) % 10000 == 0:
                logger.info(i)
                self._data_cursor.insert(rows)
                rows.clear()

            soup = BeautifulSoup(data['html'], 'html.parser')
            tr_tags = soup.find_all('tr')[1:-3]
            row = {
                '_id': data['_id'],
                'url': data['url']
            }
            for tr in tr_tags:
                text = tr.text.split('\n')
                if len(text) < 3:
                    continue
                row[text[1]] = text[2]
            rows.append(row)

        self._data_cursor.insert(rows)
        logger.info('结束')

    def to_oracle(self):
        """
        数据转移到oracle上
        :return:
        """
        logger.info('数据库存储开始')

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
        params1 = ['ID', 'PRODUCT_NAME', 'TRAD_NAME', 'SPEC', 'ZC_FORM', 'PERMIT_NO', 'PRODUCTION_UNIT', 'CODE']

        ZC_EX = ['气体', '医用氧(气态分装)', '医用氧', '医用氧(气态)', '化学药品', '医用气体', '医用气体(气态氧)', '其他', '气态', '液态和气态', '非剂型', '气态 液态',
                 '体外诊断试剂', '鼻用制剂', '液态气体', '非制剂,其他:氧', '液态', '氧(气态、液态)', '液体	', '气剂', '液态氧', '气体、液态', '医用氧(液态)',
                 '有效成份', '液态空气', '吸入性气体', '氧', '医用氧气', '氧气', '医用氧(气态、液态)', '呼吸', '其他:医用氧(气态)']
        PRODUCT_NAME_EX = ['氧', '氧(液态)', '氧(气态)', '医用液态氧', '医用氧气', '医用氧(液态)']

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
        logger.info('数据库存储结束')


if __name__ == '__main__':
    z = cfda('192.168.16.113')
    # z.parser()
    z.to_oracle()
