# -*- coding: UTF-8 -*-
import cx_Oracle
import pymysql

from python.no_work.utils import mlogger

logger = mlogger.get_defalut_logger('log/common.log', 'oracle')


class OralceCursor(object):
    def __init__(self):
        # info = 'archer/archer@localhost/minnie'
        info = 'luun/luun@192.168.16.113/sunshine'
        # info = 'kbms/kbms@192.168.5.24/orcl'
        # info = 'spiders/123456@192.168.4.30/orcl'  # 数据挖掘组数据解析支持
        self.minnie_oracle = cx_Oracle.connect(info, encoding='utf-8')
        self.oracle_cursor = self.minnie_oracle.cursor()
        if self.fechall('SELECT 1 FROM dual')[0][0] != 1:
            raise Exception('数据库连接失败')
        logger.info('数据库连接成功')

    def executeSQLParams(self, sql, params):
        try:
            count = self.oracle_cursor.execute(sql, params)
            self.minnie_oracle.commit()
            return count
        except Exception as e:
            logger.error(e)
            self.minnie_oracle.rollback()
            return 0

    def executeSQL(self, sql):
        try:
            count = self.oracle_cursor.execute(sql)
            self.minnie_oracle.commit()
            return count
        except Exception as e:
            logger.error(e)
            self.minnie_oracle.rollback()
            return 0

    def fechall(self, sql, params=None):
        if params is None:
            self.oracle_cursor.execute(sql)
        else:
            self.oracle_cursor.execute(sql, params)
        data = self.oracle_cursor.fetchall()
        return data

    def insertSQL(self, sql):
        try:
            count = self.oracle_cursor.execute(sql)
            self.minnie_oracle.commit()
            return count
        except Exception as e:
            logger.error(e)
            self.minnie_oracle.rollback()
            return 0


def insert_drug_info():
    info = 'luun/luun@192.168.16.113/sunshine'
    minnie_oracle = cx_Oracle.connect(info, encoding='utf-8')
    oraclecursor = minnie_oracle.cursor()

    minnie_mysql = pymysql.Connect(host='127.0.0.1', port=3306, user='root', passwd='minnie', db='sunshine',
                                   use_unicode=True,
                                   charset="utf8")
    mycursor = minnie_mysql.cursor()

    sql = 'SELECT * FROM DXY_DRUG_INFO'
    mycursor.execute(sql)
    data = mycursor.fetchall()

    index = 0
    for values in data:
        sql_o = "INSERT INTO DXY_DRUG_INFO \
                                (URL, blfy, ywxhzy, ywfl, cf, dlyj, zysx, yfyl, lsj, hxcf, ypmc, jj, fyyjs, ypjgfj, yyxz, FDA, pzch, OTC, lcsy, syz, jg, csmssyz, scqy,DRUG_NAME)\
                                VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20,:21,:22,:23,:24)"
        try:
            oraclecursor.execute(sql_o, values)
        except Exception as e:
            print(e)
        index += 1

    oraclecursor.close()
    mycursor.close()
    minnie_oracle.commit()
    minnie_mysql.close()
    minnie_oracle.close()


if __name__ == '__main__':
    """
        任务调度
    """
    cursor = OralceCursor()
