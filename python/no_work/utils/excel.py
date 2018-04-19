#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import pymongo
import xlwt
import xlsxwriter

from python.no_work.utils import MONGO_PORT, MONGO_IP


class WriteXLSXCustom(object):
    def __init__(self, path):
        if not str(path).endswith('.xlsx'):
            path += '.xlsx'
        self.workbook = xlsxwriter.Workbook(path)  # 建立文件
        self.format = self.get_format()
        # 建立sheet， 可以work.add_worksheet('employee')来指定sheet名，但中文名会报UnicodeDecodeErro的错误
        self.sheet = self.workbook.add_worksheet()
        # 冻结
        self.sheet.freeze_panes(row=1, col=0)

        # 列宽
        self.sheet.set_column('A:Z', 23)

    def write(self, rowindex, data):
        """

        :param rowindex: 行号
        :param data: 一行数据
        :return: 无返回值
        """
        self.sheet.set_column(firstcol=0, lastcol=100000, width=25)
        self.sheet.set_row(rowindex, 15)
        # 写入一行
        self.sheet.write_row(rowindex, 0, data, self.format)

    def get_format(self):
        """
        https://xlsxwriter.readthedocs.io/format.html#format
        :return:
        """
        _format = self.workbook.add_format()
        _format.set_align('left')
        _format.set_align('top')  # 对齐方式
        # _format.set_text_wrap()  # 自动换行
        return _format

    def close(self):
        self.workbook.close()


class WriteXLS(object):
    def __init__(self):
        """"""
        self.workbook = xlwt.Workbook()  # 创建工作簿
        self.sheet1 = self.workbook.add_sheet(u'sheet1', cell_overwrite_ok=True)  # 创建sheet
        self.mongo = pymongo.MongoClient(MONGO_IP, MONGO_PORT)

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


class Read(object):
    def __init__(self):
        """"""

