"""
# 获取相关疾病
http://pharmacy.ipmph.com/medicine/phmeddata/getInterfixIllList.action?commonName=%E9%98%BF%E8%8E%AB%E8%A5%BF%E6%9E%97&pageNo=1&pageSize=5&id=c679ee8334b640da917c91158a7b0bec
# 通过通用名称获取与同名相关的药品名称，
http://pharmacy.ipmph.com/medicine/phmeddata/getFactorySearch
# 通过ID获取数据
http://pharmacy.ipmph.com/medicine/phmeddata/getMedDirectionDetail?itype=1&sessionId=&id=c679ee8334b640da917c91158a7b0bec
"""
import datetime
import json

from urllib import parse, request, error

from bs4 import BeautifulSoup
from selenium import webdriver

from minnie.common import mlogger, moracle
from minnie.common.mfile import readFile

logger = mlogger.get_defalut_logger('pharmacy_ipmph_com.log', 'pharmacy_ipmph_com')
cursor = moracle.OralceCursor()


def parserJSON(filename):
    """
    解析首页药品类别信息，获取到具体药品名称（通用名称）。
    地址：http://pharmacy.ipmph.com/MedicineDirection.html#
    :return:
    """
    # 将json转为字典格式，获取数据
    data = json.loads(readFile(file_name=filename))
    # 输出结果
    result = []

    for d1 in data['list']:  # 一级类别
        d1_data = []
        if 'child' in d1:
            d1_data = d1['child']
        for d2 in d1_data:  # 二级类别
            d2_data = []
            if 'child' in d2:
                d2_data = d2['child']
            for d3 in d2_data:  # 药品通用名称
                result.append(d3['name'])

    return result


def request_(med_name):
    params = {
        'med_name': med_name,
        'pageNo': '1',
        'factory_name': '',
        'pageSize': '1000'
    }
    url = 'http://pharmacy.ipmph.com/medicine/phmeddata/getFactorySearch?' + \
          parse.urlencode(params).encode(encoding='utf-8').decode()

    sql = "INSERT INTO RWW_CONTENT (MED_NAME, CONTENT) VALUES (:1, :2)"

    req = request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0')
    req.add_header('X-Requested-With', 'XMLHttpRequest')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')

    try:
        response = request.urlopen(req)
    except error.HTTPError as e:
        logger.info(u'HTTPError，错误代码{code}'.format(code=e.code))
        return
    except error.URLError as e:
        logger.info(u'URLError，错误提示{reason}'.format(reason=e.reason))
        return
    except ConnectionResetError as e:
        logger.info(e)
        return

    if response is None:
        return

    cursor.executeSQLParams(sql=sql, params=[med_name, response.read().decode('utf-8')])
    # data = json.loads(response.read().decode('utf-8'))


def parserDrugJSON():
    template = ['medicineName', 'englishName', 'commonName', 'factoryName', 'suitIll',
                'pack', 'expiry', 'operative', 'pregnantDrug', 'childrenDrug',
                'approvalNumber', 'factoryInfo', 'instructionName', 'modifyDate', 'revisionDate', 'spellName',
                'mainContain', 'illness', 'character', 'usage', 'notice', 'storage', 'spec', 'toxicity', 'oldDrug',
                'medicineEffect', 'pharma', 'overdose', 'contraindication']

    sql = 'INSERT INTO RWW_INFO (MEDICINENAME, ENGLISHNAME, COMMONNAME, FACTORYNAME, SUITILL, PACK, EXPIRY, OPERATIVE, PREGNANTDRUG, CHILDRENDRUG, APPROVALNUMBER, FACTORYINFO, INSTRUCTIONNAME, MODIFYDATE, REVISIONDATE, SPELLNAME, MAINCONTAIN, ILLNESS, CHARACTER, USAGE, NOTICE, STORAGE, SPEC, TOXICITY, OLDDRUG, MEDICINEEFFECT, PHARMA, OVERDOSE, CONTRAINDICATION) VALUES (:0, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12, :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23, :24, :25, :26, :27, :28)'

    result = []
    _error = []

    for d1 in cursor.fechall('SELECT * FROM RWW_CONTENT'):

        for drug in json.loads(str(d1[1]))['list']:
            for key in template:
                if key in drug:
                    result.append(drug[key])
                else:
                    result.append('')
            if cursor.executeSQLParams(sql=sql, params=result) == 0:
                for i1, s in enumerate(result):
                    if len(s.encode('utf-8')) > 4000:
                        if i1 not in _error:
                            _error.append(i1)
            result = []

    print(_error)


def serach(serach_filed):
    sql = 'SELECT * FROM RWW_CONTENT'
    for d in cursor.fechall(sql):
        if str(d[1]).count(serach_filed) >= 1:
            print(d[0])
            return


def urllib_request(url, header):
    """
    url请求
    :param url:
    :return:
    """
    req = request.Request(url)

    for (key, value) in header.items():
        req.add_header(key, value)

    response = request.urlopen(req)

    print(
        response.read().decode('utf-8')
    )


def driver_url(url):
    """
    selenium方式
    :param url:
    :return:
    """
    driver = webdriver.Chrome(executable_path='D:\\Tech\\Tool\\chromedriver\\chromedriver.exe')
    driver.get(url=url)

    index = 1510
    while index < 0:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        index -= 1

    doc = BeautifulSoup(driver.page_source, 'html.parser')


def re1():
    """
    临床指南专家共识/医脉通网站/
    PDF下载问题
    :return:
    """
    driver = webdriver.Chrome(executable_path='D:\\Tech\\Tool\\chromedriver\\chromedriver.exe')

    # 登陆
    driver.get('http://www.medlive.cn/auth/login')
    driver.find_element_by_id('passwordDiv').click()
    username = driver.find_element_by_id('username')
    username.clear()
    username.send_keys('15958624595')

    password = driver.find_element_by_id('password')
    password.clear()
    password.send_keys('sunshine')

    driver.find_element_by_id('loginsubmit').click()

    # 资料列表
    # url = 'http://guide.medlive.cn/guideline/list'
    # driver.get(url)
    # index = 1510
    # while index < 0:
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    #     index -= 1
    # 资料详情页
    url = 'http://guide.medlive.cn/guideline/15108'
    driver.get(url)

    driver.find_element_by_link_text('下载').click()

    print(1)


def re2():
    """
    知网/临床诊疗知识库--疾病
    :return:
    """
    # 查询类别对应的疾病数量；query为类别的代码，能从html上获取；其他字段位置什么含义
    url = 'http://lczl.cnki.net/jb/search?type=类别路径&query=1/8/9&mquery=&issearch=0&isfzzljb='
    # 查询类别对应疾病的具体信息；query为类别的代码；page翻页；
    url = 'http://lczl.cnki.net/jb/getpage?page=0&type=类别路径&query=1/8/9&mquery=&isfzzljb='

    # 登陆后的操作
    # 直接获取html文件
    # url = 'http://lczl.cnki.net/jbdetail/index?query=144'
    # 获取疾病的具体属性信息，获取json数据
    # url = 'http://lczl.cnki.net/jbdetail/getdata?code=144'
    # 获取临床相关文献；vsm参数的值来资源上面这个请求
    # url = 'http://lczl.cnki.net/jbdetail/getpagedata?page=0&vsm=半乳糖血症:9217,半乳糖血:3879'


def re2():
    """
    http://ccdas.ipmph.com/rwDisease/rwDiseaseList#
    :return:
    """
    # 列表页面，直接下一页下一页
    url = 'http://ccdas.ipmph.com/rwDisease/rwDiseaseList#'


if __name__ == '__main__':
    # result = parserJSON('cn_data.json')
    # for i, name in enumerate(result):
    #     if i < 638:
    #         continue
    #     print(i, name)
    #     request_(med_name=name)
    # parserDrugJSON()
    # serach(serach_filed='74b5eb7f7cf9474f94ce190aa260e85a')
    print(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
