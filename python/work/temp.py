#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import csv
import datetime

import jieba
import pymongo

from python.no_work.utils.mlogger import mlog
from python.no_work.utils.oracle import OralceCursor

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


def get_disease_info():
    """
    获取指定疾病列表的数据 \n
    :return:
    """
    disease_names = open('D:\\Temp\\dis.txt', 'r', encoding='utf-8').read().split('#')
    datas = []

    # 1-cnki_disease_lczl
    # 2-medlive_disease
    # 3-中国知网_医学知识库_疾病
    # 4-rw_disease
    # 5-rw_disease
    disease_lib = {
        'cnki_disease_lczl': {'dbname': 'cnki_disease_lczl', 'field': 'name'},
        'medlive_disease': {'dbname': 'medlive_disease', 'field': 'name'},
        '中国知网_医学知识库_疾病': {'dbname': '中国知网_医学知识库_疾病', 'field': '【 疾病名称 】'},
        'rw_disease': {'dbname': 'rw_disease', 'field': 'title'},
        'wiki8_disease': {'dbname': 'wiki8_disease', 'field': 'name'},
    }
    for k, v in disease_lib.items():
        disease_names = get_disease_info_utils(v, disease_names)

    print(len(disease_names))

    datas.clear()

    failure_name = []
    for name in disease_names:
        if find_name_by_disease_lib(name, disease_lib):
            pass
        else:
            failure_name.append(name)

    print(failure_name)

    to_excel(disease_lib)


def get_disease_info_utils(dis, disease_names):
    """
    :param dbname: 数据库名称
    :param field:  字段
    :param disease_names: 查询值得集合
    :param datas: 数据结果集
    :return: 没有查询的值
    """
    datas = []
    excule_names = []
    cursor = mongo[dis['dbname']]['data']
    for d in cursor.find({dis['field']: {'$in': disease_names}}):
        excule_names.append(d[dis['field']])
        d['regex'] = d[dis['field']]
        d['key'] = d[dis['field']]
        datas.append(d)
    dis['datas'] = datas
    return list(set(disease_names).difference(set(excule_names)))


def find_name_by_disease_lib(name, disease_lib):
    lib = {
        'cnki_disease_lczl': {'dbname': 'cnki_disease_lczl', 'field': 'name'},
        'medlive_disease': {'dbname': 'medlive_disease', 'field': 'name'},
        '中国知网_医学知识库_疾病': {'dbname': '中国知网_医学知识库_疾病', 'field': '【 疾病名称 】'},
        'rw_disease': {'dbname': 'rw_disease', 'field': 'title'},
        'wiki8_disease': {'dbname': 'wiki8_disease', 'field': 'name'},
    }
    datas = []
    result = False
    ns = list(jieba.cut(name, cut_all=False))
    # (糖尿|2型|病){3,}
    regex = '(' + '|'.join(ns) + '){' + str(len(ns) // 2 + 1) + ',}'
    for k, v in lib.items():
        cursor = mongo[v['dbname']]['data']
        for d in cursor.find({v['field']: {'$regex': regex}}):
            result = True
            d['regex'] = regex
            d['key'] = name
            datas.append(d)
        disease_lib[k]['datas'] += datas
        datas.clear()
    return result


def to_excel(disease_lib):
    for k, v in disease_lib.items():
        if k == 'rw_disease':
            w = WriteXLSX(k)
            w.write_data(v['datas'])


def getTitle():
    lib = {
        'cnki_disease_lczl': {'dbname': 'cnki_disease_lczl', 'field': 'name'},
        'medlive_disease': {'dbname': 'medlive_disease', 'field': 'name'},
        '中国知网_医学知识库_疾病': {'dbname': '中国知网_医学知识库_疾病', 'field': '【 疾病名称 】'},
        'rw_disease': {'dbname': 'rw_disease', 'field': 'title'},
        'wiki8_disease': {'dbname': 'wiki8_disease', 'field': 'name'},
    }
    for k, v in lib.items():
        title = []
        for data in mongo[k]['data'].find():
            for k, v in data.items():
                if k not in title and not str(k).__contains__('一篇')\
                        and not str(k).__contains__('阅读：'):
                    title.append(k)
        print(title)


if __name__ == '__main__':
    """
    """
    # 工具----------------------------------------------------------------------------------
    count_url('医学百科_手术百科')
    # common_to_excel()
    # A02()
    # get_disease_info()
    # mongo_test()
    # yaozh_monitored_count()
    # yaozh_unlabeleduse_update()
    # getTitle()
