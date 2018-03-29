#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import json
import random
import traceback

import pymongo

from urllib import request, parse

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from python.no_work.utils import mlogger
from python.no_work.utils.common import getNowDate

logger = mlogger.get_defalut_logger('crawler.log', 'crawler')
USER_AGENT = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
    "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    'Mozilla/4.0(compatible;MSIE6.0;)Opera/UCWEB7.0.2.37/28/999',
    'Openwave/UCWEB7.0.2.37/28/999',
    'NOKIA5700/UCWEB7.0.2.37/28/999',
    'UCWEB7.0.2.37/28/999',
    'Mozilla/5.0(compatible;MSIE9.0;WindowsPhoneOS7.5;Trident/5.0;IEMobile/9.0;HTC;Titan)',
    'Mozilla/5.0(hp-tablet;Linux;hpwOS/3.0.0;U;en-US)AppleWebKit/534.6(KHTML,likeGecko)wOSBrowser/233.70Safari/534.6TouchPad/1.0',
    'Mozilla/5.0(BlackBerry;U;BlackBerry9800;en)AppleWebKit/534.1+(KHTML,likeGecko)Version/6.0.0.337MobileSafari/534.1+',
    'Mozilla/5.0(Linux;U;Android3.0;en-us;XoomBuild/HRI39)AppleWebKit/534.13(KHTML,likeGecko)Version/4.0Safari/534.13',
    'Opera/9.80(Android2.3.4;Linux;OperaMobi/build-1107180945;U;en-GB)Presto/2.8.149Version/11.10',
    'MQQBrowser/26Mozilla/5.0(Linux;U;Android2.3.7;zh-cn;MB200Build/GRJ22;CyanogenMod-7)AppleWebKit/533.1(KHTML,likeGecko)Version/4.0MobileSafari/533.1',
    'Mozilla/5.0(Linux;U;Android2.3.7;en-us;NexusOneBuild/FRF91)AppleWebKit/533.1(KHTML,likeGecko)Version/4.0MobileSafari/533.1',
    'Mozilla/5.0(iPad;U;CPUOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5',
    'Mozilla/5.0(iPod;U;CPUiPhoneOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5',
    'Mozilla/5.0(iPhone;U;CPUiPhoneOS4_3_3likeMacOSX;en-us)AppleWebKit/533.17.9(KHTML,likeGecko)Version/5.0.2Mobile/8J2Safari/6533.18.5',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',
    'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',
    'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',
    'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11',
    'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
    'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
    'Mozilla/4.0(compatible;MSIE6.0;WindowsNT5.1)',
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)',
    'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)',
    'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',
    'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
    'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50'
]
PROXY_IP = [
    {'ip': '192.168.16.137', 'port': '6001', 'type': 'http'},
    {'ip': '192.168.16.113', 'port': '6001', 'type': 'http'},
    {'ip': '192.168.16.158', 'port': '6001', 'type': 'http'},
    {'ip': '192.168.16.212', 'port': '6001', 'type': 'http'},
    {}
]


def getHttpStatus(browser):
    """
    字典值：url,status,statusText
    :param browser:
    :return:
    """
    for responseReceived in browser.get_log('performance'):
        try:
            _json = json.loads(responseReceived[u'message'])
            # [u'message'][u'params'][u'response']
            if 'message' in _json \
                    and 'params' in _json['message'] \
                    and 'response' in _json['message']['params']:
                response = _json['message']['params']['response']

                if response['url'] == browser.current_url \
                        and response['status'] == 200:
                    return True
                    # if response['status'] is not '200':
                    #     return False
        except BaseException as e:
            print(e)
            pass

    return False


def get_user_agent():
    r = ('User-Agent', random.choice(USER_AGENT))
    return r


class Crawler(object):
    """
    1.网络异常
    2.driver怎么判断请求成
    2018-3-27
        1.增加代理，代理需要自己部署
        2.代理更新方法
    """

    def __init__(self):
        self.__mongo = pymongo.MongoClient('192.168.16.113', 27017)
        self.__error_cursor = self.__mongo['minnie']['crawler_error']
        # 驱动器地址
        self.__executable_path = 'C:\\chromedriver.exe'
        # 日志地址
        self.__service_log_path = 'D:\\Temp\\chromdriver.log'
        # 请求次数达到一定数量，切换代理。
        self.__request_count = 1
        # 浏览器驱动
        self.driver = None
        # request驱动
        self.opener = None

        self.update_proxy()

    def driver_get_url(self, url):
        """
        selenium方式请求，浏览器\n
        请求成功更新url；存储响应的html界面
        :param url: 字符串类型\n
        :return: 长文本
        """

        # if not getHttpStatus(self.driver):
        #     return False

        try:
            self.driver.get(url)
            result = self.driver.page_source
        except TimeoutException as exception:
            result = ''
            error_info = {
                'url': url,
                'type': str(exception),
                'error': traceback.format_exc(),
                'date': getNowDate()
            }
            self.__error_cursor.insert(error_info)

        if self.__request_count % 500 == 0:
            self.update_proxy()

        self.__request_count += 1

        return result

    def request_get_url(self, url, params=None, header=None):
        """
        request方式请求\n
        :param header: 字典格式的header头 \n
        :param url: 字符串格式\n
        :param params: 字典格式\n
        :return: 长文本，或者也可以返回response，建议长文本吧
        """
        headers = {
            'User-Agent': random.choice(USER_AGENT)
        }
        if header is None:
            header = {}
        for key, value in header.items():
            headers[key] = value

        data = None
        if params:
            data = parse.urlencode(params).encode('utf-8')

        r = request.Request(url=self.format_url(url), headers=headers, data=data)
        result = None
        try:
            response = self.opener.open(r)
            result = response.read()
        # except error.HTTPError:
        #     return 'Minnie#400'
        # except IncompleteRead:
        #     logger.error(traceback.format_exc())
        # except RemoteDisconnected:
        #     关闭远程连接
        #     logger.error(traceback.format_exc())
        except BaseException as exception:
            error_info = {
                'url': url,
                'type': str(exception),
                'error': traceback.format_exc(),
                'date': getNowDate()
            }
            self.__error_cursor.insert(error_info)

        if self.__request_count % 500 == 0:
            self.update_proxy()

        self.__request_count += 1

        return result

    @staticmethod
    def format_url(url):
        """
        检测url中是否包含中文，包含中文的话需要编码解码
        将中文转换为二进制
        :param url:
        :return:
        """
        if not url.__contains__('?'):
            return url

        index1 = url.index('?')
        domain = url[0: index1]
        raw_params = url[index1 + 1:]

        format_params = {}
        for p in raw_params.split('&'):
            temp = p.split('=')
            format_params[temp[0]] = temp[1]

        return domain + '?' + str(parse.urlencode(format_params).encode('utf-8').decode('utf-8'))

    def update_proxy(self):
        proxy_ip = random.choice(PROXY_IP)
        logger.info(proxy_ip)
        # 退出
        if self.driver:
            self.driver.quit()
        # 获取新的驱动器
        self.driver = self.new_driver(proxy_ip)

        if proxy_ip:
            # 代理设置
            proxy = request.ProxyHandler({proxy_ip['type']: proxy_ip['ip'] + ':' + proxy_ip['port']})
            self.opener = request.build_opener(request.HTTPHandler, proxy)
            self.opener.addheaders = [get_user_agent()]
            request.install_opener(opener=self.opener)

    def new_driver(self, proxy_ip=None):
        options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        if proxy_ip:
            options.add_argument(
                '--proxy-server={http}://{ip}:{port}'.format(http=proxy_ip['type'],
                                                             ip=proxy_ip['ip'],
                                                             port=proxy_ip['port']))

        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities['loggingPrefs'] = {'performance': 'ALL'}

        driver = webdriver.Chrome(executable_path=self.__executable_path,
                                  chrome_options=options,
                                  desired_capabilities=desired_capabilities,
                                  service_log_path=self.__service_log_path)
        driver.implicitly_wait(5)
        return driver

    def refresh(self):
        if self.driver:
            self.driver.refresh()


if __name__ == '__main__':
    c = Crawler()
    check_url = 'https://bbs.yaozh.com/template/eis_c_m1/img/agree.gif'
    c.driver_get_url(check_url)
    c.request_get_url(check_url)
    print(1)
