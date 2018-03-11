#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import random
import time
import re

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium import webdriver

from minnie.common import mlogger, moracle

logger = mlogger.get_defalut_logger('CFDA.log', 'CFDA')


class Crawler:
    def __init__(self):
        # 初始化database,获取游标
        self.cursor = moracle.OralceCursor()
        self.driver = webdriver.Chrome(executable_path='D:\\Tech\\Tool\\chromedriver\\chromedriver.exe')

    def create_table(self):
        """
        初始化表
        :return:
        """
        # 存储CFDA药品访问详情页面的信息
        sql = """
            CREATE TABLE CFDA_DRUG_URL
            (
              PAGE        VARCHAR2(255),
              TEXT        VARCHAR2(1000),
              HREF        VARCHAR2(255),
              TYPE        VARCHAR2(255),
              CREATE_TIME DATE DEFAULT SYSDATE
            );
        """
        self.cursor.executeSQL(sql)

        sql = """
            CREATE TABLE CFDA_DRUG_URL_CODE_BAK
                (
                  CODE        VARCHAR2(255),
                  STA_CODE    VARCHAR2(2000),
                  PAGE        VARCHAR2(255),
                  TEXT        VARCHAR2(1000),
                  HREF        VARCHAR2(255),
                  TYPE        VARCHAR2(255),
                  IS_ENABLE VARCHAR2(1) DEFAULT 0,
                  CREATE_TIME DATE DEFAULT SYSDATE
                )
        """
        self.cursor.executeSQL(sql)

        sql = """
            CREATE TABLE CFDA_DRUG_HTML (
              CODE        VARCHAR2(255),
              TYPE        VARCHAR2(255),
              HTML        CLOB,
              CREATE_TIME DATE DEFAULT SYSDATE
            )
        """
        self.cursor.executeSQL(sql)

        sql = """
            CREATE TABLE CFDA_DRUG_GC_INFO (
              STA_CODE           VARCHAR2(15),
              PRODUCT_NAME       VARCHAR2(255),
              EN_NAME            VARCHAR2(255),
              TRAD_NAME          VARCHAR2(255),
              DRUG_FORM          VARCHAR2(255),
              SPEC               VARCHAR2(4000),
              PRODUCTION_UNIT    VARCHAR2(255),
              PRODUCTION_ADDRESS VARCHAR2(255),
              DRUG_TYPE          VARCHAR2(255),
              PZWH               VARCHAR2(255),
              PZRQ               VARCHAR2(255),
              OLD_PZWH           VARCHAR2(255),
              STA_NOTE           VARCHAR2(4000)
            )
        """
        self.cursor.executeSQL(sql)

        sql = """
            CREATE TABLE CFDA_DRUG_JK_INFO (
              REGISTRATION_NUMBER     VARCHAR2(255),
              OLD_REGISTRATION_NUMBER VARCHAR2(255),
              REGISTRATION_NUMBER_NOTE VARCHAR2(4000),
              SUBPACKAGE_PZWH VARCHAR2(255),
              COMPANY_CN VARCHAR2(255),
              COMPANY_EN VARCHAR2(255),
              COMPANY_ADDRESS_CN VARCHAR2(255),
              COMPANY_ADDRESS_EN VARCHAR2(255),
              COUNTRY_CN VARCHAR2(255),
              COUNTRY_EN VARCHAR2(255),
              PRODUCT_NAME_EN VARCHAR2(255),
              PRODUCT_NAME_CN VARCHAR2(255),
              TRAD_NAME_EN VARCHAR2(255),
              TRAD_NAME_CN VARCHAR2(255),
              DRUG_FORM VARCHAR2(255),
              SPEC VARCHAR2(4000),
              PACKAGE_SPEC VARCHAR2(255),
              PRODUCTION_UNIT_CN VARCHAR2(255),
              PRODUCTION_UNIT_EN VARCHAR2(255),
              PRODUCTION_UNIT_ADDRESS_CN VARCHAR2(255),
              PRODUCTION_UNIT_ADDRESS_EN VARCHAR2(255),
              PRODUCTION_UNIT_COUNTRY_CN VARCHAR2(255),
              PRODUCTION_UNIT_COUNTRY_EN VARCHAR2(255),
              CERTIFICATE_DATE VARCHAR2(255),
              ENABLE_DATE VARCHAR2(255),
              SUBPACKAGE_COMPANY_NAME VARCHAR2(255),
              SUBPACKAGE_COMPANY_ADDRESS VARCHAR2(255),
              SUBPACKAGE_COMPANY_PZWH_DATE VARCHAR2(255),
              DRUG_TYPE VARCHAR2(255),
              STA_CODE VARCHAR2(4000)
            )
        """
        self.cursor.executeSQL(sql)

    def drug_info_url(self, url, page, type):
        """
        1.获取进口药品，国产药品的列表；
        2.只爬取当前page的数据，并且将其存储；
        :param type: 国产-1 or 进口-2
        :param url:
        :param page: 页数
        :return:
        """
        # TYPE == 国产-1 or 进口-2
        sql = "INSERT INTO CFDA_DRUG_URL (HREF, TEXT, PAGE, TYPE) VALUES (:1, :2, :3, :4)"
        url += str(page)
        self.driver.get(url=url)
        a_ele = self.driver.find_elements_by_tag_name('a')
        for a in a_ele:
            href = a.get_attribute('href')
            text = a.text
            params = [href, text, page, type]
            self.cursor.executeSQLParams(sql, params)

    def execute_drug_info_url_GC(self):
        """
        国产药品列表
        :return:
        """
        url = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=25&curstart='
        page = 1
        while True:
            self.drug_info_url(url, page, 1)
            page += 1
            time.sleep(1.5)
            if page == 11022:
                break

    def executeDrugInfoUrlJK(self):
        """
        进口药品列表
        :return:
        """
        url = 'http://app1.sfda.gov.cn/datasearch/face3/search.jsp?tableId=36&curstart='
        page = 275
        while True:
            self.drug_info_url(url, page, 2)
            page += 1
            time.sleep(1.5)
            if page == 276:
                break

    def pumpDrugCode(self):
        """
        1.将url中的编码提取出来，重新放到一个表中，因为update太慢，insert比较快。
        2.抽取本位码
        3.抽取请求链接
        [\u4e00-\u9fa5]+公司
        86[0-9]{12}本位码
        国[\u4e00-\u9fa5]+[A-Z0-9]+|[A-Z0-9]+

        :return:
        """
        sql = 'SELECT PAGE,TEXT,HREF,TYPE FROM CFDA_DRUG_URL'
        insert_sql = 'INSERT INTO CFDA_DRUG_URL_CODE_BAK (CODE, STA_CODE, PAGE, TEXT, HREF, TYPE) VALUES (:1, :2, :3, :4, :5, :6)'
        datas = self.cursor.fechall(sql=sql)
        index = 0
        for data in datas:
            index += 1
            if index % 1000 == 0:
                logger.info(index)
            # CFDA药品唯一标识
            c = re.findall('(&Id=[0-9]+)', data[2])[0].replace('&Id=', '')
            # 请求连接截取
            href = re.findall('(\'.*\')', data[2])[0].replace('\'', '')
            # 本位码拼接
            standardcode = ",".join(re.findall('86[0-9]{12}', data[1]))
            params = [c, standardcode, data[0], data[1], href, data[3]]
            self.cursor.executeSQLParams(sql=insert_sql, params=params)

    def drugInfo(self):
        """
        获取详情信息
        :param url:
        :return:
        """
        base_url = 'http://app1.sfda.gov.cn/datasearch/face3/'
        sql = "SELECT CODE, PAGE,HREF, TYPE FROM CFDA_DRUG_URL_CODE WHERE CODE NOT IN (SELECT CODE FROM CFDA_DRUG_HTML WHERE CFDA_DRUG_HTML.TYPE = '1') AND TYPE = '1' ORDER BY TO_NUMBER(PAGE)"
        update_sql = "UPDATE CFDA_DRUG_URL_CODE SET IS_ENABLE = '1' WHERE CODE = :1 AND PAGE = :2 "
        insert_sql = "INSERT INTO CFDA_DRUG_HTML (CODE, TYPE, HTML) VALUES (:1, :2, :3)"
        datas = self.cursor.fechall(sql=sql)
        for data in datas:
            time.sleep(random.random() * 20)
            url = base_url + data[2]
            logger.info(url)
            try:
                self.driver.get(url=url)
            except TimeoutException as timeout:
                logger.error("连接超时-{url}".format(url=url))
                time.sleep(600)
                continue
            html = self.driver.page_source
            self.cursor.executeSQLParams(sql=insert_sql, params=[data[0], data[3], html])
            self.cursor.executeSQLParams(sql=update_sql, params=[data[0], data[1]])
        return

    def formatGC(self):
        """
        格式化CFDA国产药品的详情信息
        http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=25&tableName=TABLE25&tableView=%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81&Id=156585
        :return:
        """
        sql = "SELECT CODE,TYPE,HTML FROM CFDA_DRUG_HTML WHERE TYPE = '1' AND CREATE_TIME > TO_DATE('2017-12-05 09:09:00', 'yyyy-mm-dd hh24:mi:ss')"
        insert_sql = "INSERT INTO CFDA_DRUG_GC_INFO (ID, PZWH, PRODUCT_NAME, EN_NAME, TRAD_NAME, DRUG_FORM, SPEC, PRODUCTION_UNIT, PRODUCTION_ADDRESS, DRUG_TYPE, PZRQ, OLD_PZWH, STA_CODE, STA_NOTE) VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14)"
        datas = self.cursor.fechall(sql=sql)
        for data in datas:
            doc = BeautifulSoup(data[2], 'html.parser')
            tr_el = doc.find_all('tr')[1:-4]  # -3还是-4还需要进行测试调整下  TODO
            info_params = [data[0] + '-' + data[1]]
            for tr in tr_el:
                # TODO 需要测试tr是否未trg类型的

                # 把药品信息增加到list集合中，依次排序；sql插入，当参数使用
                info_params.append(tr.find_all('td')[1].text)

            self.cursor.executeSQLParams(insert_sql, info_params)
            info_params.clear()
        return

    def formatJK(self):
        """
        http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=36&tableName=TABLE36&tableView=%E8%BF%9B%E5%8F%A3%E8%8D%AF%E5%93%81&Id=16187
        :return:
        """
        sql = "SELECT CODE,TYPE,HTML FROM CFDA_DRUG_HTML WHERE TYPE = '2'"
        insert_sql = "INSERT INTO CFDA_DRUG_JK_INFO (ID, REGISTRATION_NUMBER, OLD_REGISTRATION_NUMBER, REGISTRATION_NUMBER_NOTE, SUBPACKAGE_PZWH, COMPANY_CN, COMPANY_EN, COMPANY_ADDRESS_CN, COMPANY_ADDRESS_EN, COUNTRY_CN, COUNTRY_EN, PRODUCT_NAME_EN, PRODUCT_NAME_CN, TRAD_NAME_EN, TRAD_NAME_CN, DRUG_FORM, SPEC, PACKAGE_SPEC, PRODUCTION_UNIT_CN, PRODUCTION_UNIT_EN, PRODUCTION_UNIT_ADDRESS_CN, PRODUCTION_UNIT_ADDRESS_EN, PRODUCTION_UNIT_COUNTRY_CN, PRODUCTION_UNIT_COUNTRY_EN, CERTIFICATE_DATE, ENABLE_DATE, SUBPACKAGE_COMPANY_NAME, SUBPACKAGE_COMPANY_ADDRESS, SUBPACKAGE_COMPANY_PZWH_DATE, SUBPACKAGE_COMPANY_PZWH_ENABLE, DRUG_TYPE, STA_CODE, STA_NOTE) VALUES (:1, :2, :3,:4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28, :29, :30, :31, :32, :33)"
        datas = self.cursor.fechall(sql=sql)
        for data in datas:
            doc = BeautifulSoup(data[2], 'html.parser')
            tr_el = doc.find_all('tr')[1:-4]  # -3还是-4还需要进行测试调整下  TODO
            info_params = [data[0] + '-' + data[1]]
            for tr in tr_el:
                # TODO 需要测试tr是否未trg类型的

                # 把药品信息增加到list集合中，依次排序；sql插入，当参数使用
                info_params.append(tr.find_all('td')[1].text)

            self.cursor.executeSQLParams(insert_sql, info_params)
            info_params.clear()
        return


if __name__ == '__main__':
    c = Crawler()
    # c.formatJK()
    c.formatGC()
