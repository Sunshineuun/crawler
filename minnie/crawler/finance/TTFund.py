#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 天天基金网站：http://fund.eastmoney.com/
# 文件日志处理器
import datetime
from urllib import request

from bs4 import BeautifulSoup

from minnie.common import moracle
from minnie.common import mlogger

logger = mlogger.get_defalut_logger('finance.log', 'finance')
cursor = moracle.OralceCursor()

class TTJJ:
    """
    天天基金网络
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'cookie': 'ad_download=1; UtzD_f52b_saltkey=eX2d3U52; UtzD_f52b_lastvisit=1509675175; yaozh_uidhas=1; '
                      'yaozh_mylogin=1509678803; UtzD_f52b_ulastactivity=1509678775%7C0; '
                      'PHPSESSID=e9rb4o3833pie2aatt1l5s53l1; WAF_SESSION_ID=f84c0abc221ed3c6c24ab4b93e46f20d; '
                      'yaozh_logintime=1509946862; yaozh_user=418772%09sunshine_; db_w_auth=401170%09sunshine_; '
                      'UtzD_f52b_lastact=1509946863%09uc.php%09; '
                      'UtzD_f52b_auth=d8c6QRnQMAt9zw'
                      '%2FcKuETMRycD0tfDLd1ffNCb2qABk93jJ3i1obFPtKtza8smm3xRCfr714pM6PNizj1BikERZYeaJ8; '
                      '_ga=GA1.2.1934179620.1509678742; _gid=GA1.2.919494381.1509946857; '
                      '_ga=GA1.3.1934179620.1509678742; Hm_lvt_65968db3ac154c3089d7f9a4cbb98c94=1509678743,'
                      '1509795818,1509860494,1509929876; Hm_lpvt_65968db3ac154c3089d7f9a4cbb98c94=1509946875 '
        }
        self.opener = request.build_opener(request.HTTPHandler)
        request.install_opener(opener=self.opener)

    def fund_net_value(self):
        """
        通过code（基金代码），per（pagesize)抓取基金净值
        :return:
        """
        codes = cursor.fechall(
            'SELECT * FROM FUND_OPENFUNDNETVALUE WHERE FUND_CODE NOT IN (SELECT FUND_CODE FROM FUND_NET_VALUE_HISTORY GROUP BY FUND_CODE)')

        for c in codes:
            try:
                code = c[0]
                if code.__len__() != 6 and code.isdigit():
                    logger.info('基金编码错误')
                url = 'http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code={code}&page=1&per={per}&sdate=&edate=&rt=0.12943809324335898'
                # 传递参数
                url = url.format(code=code, per=5000)
                r = request.Request(url=url, headers=self.headers)
                response = self.opener.open(r)

                if response.code != 200:
                    logger.info('请求失败{url},响应码{code}'.format(url=url, code=response.code))
                    return

                html = response.read().decode('utf-8')
                response.close()
                doc = BeautifulSoup(html, 'html.parser')
                trs = doc.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')
                    # Net Asset Value（NAV）单位净值
                    # Cumulative net 累积净值
                    # growth rate 增长率
                    # redemption 赎回
                    # subscribe 申购
                    if len(tds) == 0:
                        continue
                    sql = """INSERT INTO FUND_NET_VALUE_HISTORY (FUND_CODE, FUND_DATE, NAV, NC, GROWTHRATE, SUBSCRIBE, REDEMPTION) VALUES
                                      ('%s','%s','%s','%s','%s','%s','%s')
                                            """ % (
                        code, tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text, tds[5].text)
                    cursor.insertSQL(sql=sql)
            except Exception as e:
                logger.error(e)
                logger.error(c[0])

    def openFundNetValue(self):
        """
        每天抓取净值
        :return:
        """
        sql = "INSERT INTO FUND_OPENFUNDNETVALUE_DAY (FUND_CODE, FUND_NAME, FUND_NAME_PY, REDEMPTION, SUBSCRIBE, SERVICE_CHARGE, PURCHASE_STATR) VALUES (:1, :2, :3, :4, :5, :6, :7)"
        url = 'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=1&letter=&gsid=&text=&sort=zdf,desc&page=1,9999&feature=|&dt=1511001316637&atfc=&onlySale=0'
        response = request.urlopen(url)
        content = response.read().decode('UTF-8')[100:-139]
        c = str(content).split('],[')
        for t in c:
            t1 = t.replace('"', '').split(',')
            params = [t1[0], t1[1], t1[2], t1[9], t1[10], t1[17], t1[12]]
            cursor.executeSQLParams(sql=sql, params=params)

    def open_fundNet_value_day(self):
        """
        基金净值抓取
        :return:
        """
        sql = """INSERT INTO FUND_NET_VALUE_HISTORY (FUND_CODE, FUND_DATE, NAV, NC, GROWTHRATE, SUBSCRIBE, REDEMPTION) VALUES
                                              (:1, :2, :3, :4, :5, :6, :7)
                                                    """
        _date = datetime.datetime.now().strftime('%Y-%m-%d')
        url = 'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx?t=1&lx=1&letter=&gsid=&text=&sort=zdf,desc&page=1,9999&feature=|&dt=1511001316637&atfc=&onlySale=0'
        response = request.urlopen(url)
        content = response.read().decode('UTF-8')[100:-139]
        c = str(content).split('],[')
        for t in c:
            t1 = t.replace('"', '').split(',')
            params = [t1[0], _date, t1[3], t1[4], t1[8] + '%', t1[9], t1[10]]
            cursor.executeSQLParams(sql=sql, params=params)

    def fundSituation(self):
        codes = cursor.fechall('SELECT * FROM FUND_OPENFUNDNETVALUE')
        for code in codes:
            url = 'http://fund.eastmoney.com/f10/jbgk_{code}.html'
            # 传递参数
            url = url.format(code=code[0])
            r = request.Request(url=url, headers=self.headers)
            try:
                response = self.opener.open(r)
            except Exception as e:
                logger.error("{code},{e}".format(e=e, code=code[0]))
                continue
            content = response.read().decode('utf-8')
            doc = BeautifulSoup(content)
            # 获取简介信息
            tds = doc.find_all('td')
            params = []
            for td in tds:
                params.append(td.text)

            # 获取其它描述信息
            div = doc.find_all('div', class_='boxitem w790')
            other = ''
            for d in div:
                other += d.text + '#'
            params.append(other)

            sql = """
                INSERT INTO FUND_GENERAL_SITUATION (FUND_CODE, FULL_NAME, SHORTCUT_NAME, FUND_TYPE, ISSUING_DATE, DATE_AND_SCALE, ASSET_SIZE, SHARE_SIZE, CUSTODIAN, TRUSTEE, HANDLER, PARTICIPATION_PROFIT, MANAGE_CHARGE, TRUSTEE_CHARGE, SELL_SERVICE_CHARGE, HIGH_SUBSCRIBE, HIGH_REDEMPTION, HIGH_SUBSCRIBE2, PERFORMANCE_EVALUATION, TAIL_AFTER, OTHER) VALUES
                  (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21)
            """
            cursor.executeSQLParams(sql, params)
            print(1)


if __name__ == '__main__':
    pass