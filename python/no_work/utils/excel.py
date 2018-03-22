#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import pymongo
import xlwt
import xlsxwriter
import re


class WriteXLS(object):
    def __init__(self):
        """"""
        self.workbook = xlwt.Workbook()  # 创建工作簿
        self.sheet1 = self.workbook.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet
        self.mongo = pymongo.MongoClient('192.168.16.113', 27017)

    def write(self, _dbname, _tname, path):
        title = self.get_title(_dbname, _tname)
        row = -1
        for data in self.mongo[_dbname][_tname].find():
            row += 1
            column = -1
            for k in title:
                column += 1
                if k in data:
                    # write的第一个,第二个参数时坐标, 第三个是要写入的数据
                    self.sheet1.write(row, column, str(data[k]))
        self.workbook.save(path)

    def get_title(self, _dbname, _tname):
        """
        :param _dbname: 数据库名称
        :param _tname: 表名称
        :return:
        """
        cursor = self.mongo[_dbname][_tname]
        title = []
        for data in cursor.find():
            for k, v in data.items():
                if k not in title:
                    title.append(k)
        return title


class WriteXLSX(object):
    def __init__(self, path='temp.xlsx'):
        self.workbook = xlsxwriter.Workbook(path)  # 建立文件
        self.format = self.get_format()
        # 建立sheet， 可以work.add_worksheet('employee')来指定sheet名，但中文名会报UnicodeDecodeErro的错误
        self.sheet = self.workbook.add_worksheet()
        self.sheet.set_column('A:Z', 35)
        # self.sheet.set_default_row(45)
        self.mongo = pymongo.MongoClient('192.168.16.113', 27017)

    def write(self, _dbname, _tname, title=None):
        if not title:
            title = self.get_title(_dbname, _tname)

        self.write_title(title)
        row = 0
        for data in self.mongo[_dbname][_tname].find({'药品本位码':{'$exists':'true'},'$where':"(this.药品本位码.length > 25)"}):
            row += 1
            column = -1
            for k in title:
                column += 1
                if k in data:
                    # write的第一个,第二个参数时坐标, 第三个是要写入的数据
                    self.sheet.write(row, column, replace(data[k]), self.format)
        self.workbook.close()

    def write_title(self, title):
        column = -1
        for t in title:
            column += 1
            self.sheet.write(0, column, t)

    def get_title(self, _dbname, _tname):
        """
        :param _dbname: 数据库名称
        :param _tname: 表名称
        :return:
        """
        cursor = self.mongo[_dbname][_tname]
        title = []
        for data in cursor.find():
            for k, v in data.items():
                if k not in title:
                    title.append(k)
        return title

    def get_format(self):
        """
        https://xlsxwriter.readthedocs.io/format.html#format
        :return:
        """
        _format = self.workbook.add_format()
        _format.set_align('vjustify')
        _format.set_align('top')
        _format.set_text_wrap()
        return _format


class Read(object):
    def __init__(self):
        """"""


def replace(s):
    """"""
    return str(s).replace('/n', '').replace('   ', '')


def get_title(_dbname, _tname):
    """
    :param _dbname: 数据库名称
    :param _tname: 表名称
    :return:
    """
    cursor = pymongo.MongoClient('192.168.16.113', 27017)[_dbname][_tname]
    title = []
    for data in cursor.find():
        for k, v in data.items():
            if k not in title:
                title.append(k)
    return title


if __name__ == '__main__':
    w = WriteXLSX(path='D://Temp//aa.xlsx')
    w.write('cfda', 'data')
    pass
