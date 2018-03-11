#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
from bs4 import BeautifulSoup

from minnie.common import moracle
from minnie.common.mfile import *


def FH():
    """
    飞华健康，解析疾病别名
    :return:
    """
    cu = moracle.OralceCursor()

    datas = cu.fechall('SELECT NAME, HTML FROM QSM_FH_08_JIBING1')

    for d in datas:
        if d[1]:
            doc = BeautifulSoup(d[1], 'html.parser')
            dise01 = doc.find(class_='dise01')
            span = dise01.find('span')  # 别名所在标签获取
            if span:
                print(
                    d[0] + '-' + span.text
                )
        else:
            print(d[0] + '===============================')


def JBK():
    """
    疾病百科，解析疾病别名
    :return:
    """
    file_path = 'D:\\Resource\\192.168.17.192\\数据爬取支持\\JBK\\JB-JB-DETAIL\\'
    files = getDirAllFilePath(file_path)
    index = 0
    for f in files:
        doc = BeautifulSoup(readFile(f), 'html.parser')
        div = doc.find(class_='tit clearfix')
        if div:
            h1 = div.find('h1')
            h2 = div.find('h2')
            if h2:
                print(
                    h1.text + '-' + h2.text
                )


def parseHTML():
    filepath = 'D:\Temp\source.html'
    doc = BeautifulSoup(readFile(filepath), 'html.parser')
    a_tags = doc.find(id='outline').find_all('a')
    page_container = str(doc.find(id='page-container').text).replace(' ', '').replace('\n', '').replace('\r', '')
    end_index = len(a_tags)
    print(
        '共有字符' + str(len(page_container)) + '个！'
    )
    for i, a in enumerate(a_tags):
        start = page_container.find(a.text.replace(' ', ''))
        if end_index <= i + 1:
            end = len(page_container)
        else:
            end = page_container.find(a_tags[i + 1].text.replace(' ', ''))

        print(
            'start >>' + str(start),
            'end >> ' + str(end),
            a.text + '>>>>>>>>>>>>' + page_container[start:end]
        )


if __name__ == '__main__':
    import datetime

    d1 = datetime.datetime(2018, 2, 20)
    d2 = datetime.datetime(2021, 2, 20)
    print(
        (d2 - d1).days
    )
