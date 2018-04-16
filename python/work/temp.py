#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import csv
import datetime
import json

import pymongo
from bs4 import BeautifulSoup

from python.no_work.crawler.realty import LianJia
from python.no_work.utils.excel import WriteXLSX, common_to_excel
from python.no_work.utils.mlogger import mlog
from python.no_work.utils.mongodb import MongodbCursor
from python.no_work.utils.crawler import Crawler
from python.no_work.utils.oracle import OralceCursor
from python.work.crawler import rw, medlive, wiki8
from python.work.crawler.yaozh import yaozh_monitored, yaozh_zy, yaozh_unlabeleduse, yaozh_zyfj
from python.work.crawler.zyfj import cnki
from python.work.crawler.zyfj.zhongyaofangji import zhongyaofangji

mongo = pymongo.MongoClient('192.168.5.94', 27017)
log = mlog


def get_key(dbname):
    cursor = mongo[dbname]['data']
    title = []
    for data in cursor.find():
        for k, v in data.items():
            if k not in title:
                title.append(k)
    print(title)
    return title


def count_url(name):
    """
    统计以抓取未抓取的url地址
    :param name:
    :param ip:
    :return:
    """
    html_cursor = mongo[name]['html']
    url_cursor = mongo[name]['url']
    data_cursor = mongo[name]['data']

    print('html-总数:', html_cursor.find().count())
    print('url-总数:', url_cursor.find().count())
    print('url-未抓取:', url_cursor.find({'isenable': '1'}).count())
    print('url-已抓取:', url_cursor.find({'isenable': '0'}).count())
    print('data-解析的数量', data_cursor.find().count())


def yaozh_monitored_count():
    """
    统计每个月的数量
    :return:
    """
    cursur = mongo['yaozh_monitored']['data']
    end = datetime.datetime.now()
    year = 2015
    month = 8
    while True:
        month += 1
        if month > 12:
            month = 1
            year += 1
        start = datetime.datetime(year, month, 1)
        print(
            start.strftime('%Y-%m'),
            cursur.find({'日期': {'$regex': start.strftime('%Y-%m')}}).count()
        )
        if start > end:
            break


def yaozh_unlabeleduse_update():
    cursor = mongo['yaozh_unlabeleduse']['url']
    print(
        cursor.remove({'url_': {'$exists': 'true'}})
    )
    print(
        cursor.update({'isenable': '0'}, {'$set': {'isenable': '1'}}, multi=True)
    )


def mongo_test():
    """"""
    # 数据库列表
    print('数据库列表')
    print(mongo.list_database_names())
    db = mongo['minnie_test']
    c1 = db['1']
    c2 = db['2']
    a = {'test': 'test'}
    c1.insert(a)
    c2.insert(a)
    # print(db.collection_names())
    print(type(json.dumps('{\'1\':\'1\'}')))


def a():
    url = mongo['yaozh_zyfj']['url']
    html = mongo['yaozh_zyfj']['html']
    result_list = []
    for i in range(35000):
        result_list.append({
            'url': 'https://db.yaozh.com/fangji/{code}.html'.format(code=10000001 + i),
            'type': '药智网-中药方剂',
            'isenable': '1'
        })
    # print(url.insert(result_list))
    for h in html.find():
        print(url.update({'url': h['url']}, {'$set': {'isenable': '0'}}))


def A02():
    oracle = OralceCursor()
    sql1 = 'SELECT * FROM KBMS_DRUG_FROM_SX WHERE ID IN :1'
    sql = "UPDATE KBMS_DRUG_FROM_SX SET ATC_CODE = :1, GENERIC_NAME = :2, DRUG_ID = :3, ML_FORM = :4, ZC_FORM = :5, UPDATE_DATE = SYSDATE  WHERE ID IN"
    index = 0
    for row in csv.reader(open('D:/aaa.csv', encoding='utf-8')):
        index += 1
        if index % 1000 == 0:
            log.info(index)
        # for id in row[5].split('#'):
        #     print(id)

        a = row[5].split('#')
        for i in range(1, len(a) // 200 + 2):
            b = a[(i - 1) * 200: i * 200]
            oracle.executeSQLParams(sql + '(\'' + '\',\''.join(b) + '\')', row[:5])
            # c = oracle.fechall(sql1, ["('86900475000058')"])


if __name__ == '__main__':
    """
    """
    # A02()

    # zhongyaofangji(ip='192.168.5.94')

    # 疾病
    # wiki8.disease('192.168.5.94')
    # w = WriteXLSX(path='D://Temp//医学百科_疾病百科_wiki8_disease.xlsx')
    # w.write('wiki8_disease', 'data')

    # w = cnki.disease_lczl('192.168.5.94')
    # w = WriteXLSX(path='D://Temp//中国知网临床诊疗知识库-疾病.xlsx')
    # w.write('cnki_disease_lczl', 'data')

    # # cnki1 = cnki.disease_pmmp('192.168.5.94')
    # w = WriteXLSX(path='D://Temp//中国知网医学知识库-疾病.xlsx')
    # w.write('中国知网_医学知识库_疾病', 'data')
    cnki.operation_pmmp('192.168.5.94').to_excel()

    cnki.operation_lczl('192.168.5.94').to_excel()

    cnki.diagnostic_examination('192.168.5.94').to_excel()

    # count_url('zhongyaofangji')
    # common_to_excel()

    # mongo_test()
    # yaozh_monitored_count()
    # y = yaozh_zy(ip='192.168.5.94')
    # y.parser()
    # w = WriteXLSX(path='D://Temp//药智网_中药药材_yaozh_zy.xlsx')
    # w.write('yaozh_zy', 'data')

    # y1 = yaozh_zyfj(ip='192.168.5.94')
    # y1.parser()

    # y2 = yaozh_interaction(ip='192.168.16.113')
    # y2.parser()
    # w = WriteXLSX(path='D://Temp//药智网_药品相互作用_interaction.xlsx')
    # w.write('yaozh_interaction', 'data')

    # y3 = yaozh_monitored('192.168.5.94')
    # y3.startup()
    # w = WriteXLSX(path='D://Temp//药智网_辅助与重点监控用药_yaozh_monitored.xlsx')
    # w.write('yaozh_monitored', 'data')

    # y4 = yaozh_unlabeleduse('192.168.5.94')
    # y4.startup()
    # w = WriteXLSX(path='D://Temp//药智网_超说明书_yaozh_unlabeleduse.xlsx')
    # w.write('yaozh_unlabeleduse', 'data')

    # yaozh_unlabeleduse_update()

    # r = rw.disease('192.168.5.94')
    # r.parser()
    # w = WriteXLSX(path='D://Temp//人卫临床助手_疾病.xlsx')
    # w.write('rw_disease', 'data')

    # m = medlive.disease('192.168.5.94')
    # m.startup()
    # w = WriteXLSX(path='D://Temp//医脉通_疾病.xlsx')
    # w.write('medlive_disease', 'data')

    # a = mongo['a']['a']
    # for i in range(5):
    #     a.update({}, {'1': 'a', '2': 'a', '3': 'a'})
    # a1 = {'1': 'a', '2': 'a', '3': 'a'}
    # a(a1)
    # print(a1)
    # get_key('cfda')
    # count_url('cfda1')
    # count_url('cfda')
    # proxy()
    # content2 = []
    # mongo = MongodbCursor('192.168.16.113')
    # cursor = mongo.get_cursor('zhongyaofangji', 'data')
    # for data in cursor.find():
    #     t = re.sub('《.*》', '', data['name'])
    #     if t not in content2:
    #         content2.append(t)
    #
    # result = []
    # for d in readFile('D:/1.txt').split(','):
    #     if d not in content2:
    #         result.append(d)
    # print(
    #     re.sub('《.*》', '', '《111》222')
    # )
