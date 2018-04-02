# -*- coding: UTF-8 -*-
import cx_Oracle
import pymysql

from python.no_work.utils import mlogger, ORACLE_INFO

logger = mlogger.get_defalut_logger('log/common.log', 'oracle')


class OralceCursor(object):
    def __init__(self):
        self.minnie_oracle = cx_Oracle.connect(ORACLE_INFO, encoding='utf-8')
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


if __name__ == '__main__':
    """
        任务调度
    """
    cursor = OralceCursor()
