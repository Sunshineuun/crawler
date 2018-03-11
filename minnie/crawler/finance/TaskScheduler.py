#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from minnie.common import mlogger
from minnie.crawler.finance.DFStock import DFCF
from minnie.crawler.finance.TTFund import TTJJ

logger = mlogger.get_defalut_logger('finance.log', 'finance')


class Quartz:
    def __init__(self):
        self.dfcf = DFCF()
        self.ttjj = TTJJ()

    def quartz1(self):
        """
            1.定时抓取数据
                1.1每日情况 - get_stock_info_day；
                1.2每日分时图 - get_time_division_codes；
        """
        logger.info("任务启动")
        self.ttjj.open_fundNet_value_day()
        self.dfcf.get_time_division_codes()
        self.dfcf.get_stock_info_day()

    def start(self):
        """
        启动任务
        :return:
        """
        scheduler = BlockingScheduler()
        """
            参考地址：http://apscheduler.readthedocs.io/en/v3.3.0/modules/triggers/cron.html#module-apscheduler.triggers.cron
            trigger-触发器模式，具体模式如下：
                1.cron:cron风格的任务触发
                    1.1dat_of_week:mon-fro
                    1.2hour:小时
                    1.3minutes:分钟
                    1.4second:miao
                2.date:固定日期触发器：任务只运行一次，运行完毕自动清除；若错过指定运行时间，任务不会被创建
                3.interval:时间间隔触发器

        """
        logger.info('任务启动')
        cron1 = CronTrigger(day_of_week='mon-fri', hour='23', minute='40', second='10')

        scheduler.add_job(self.quartz1, trigger=cron1, id='cron1')
        scheduler.start()


if __name__ == '__main__':
    """
        1.It will automatically build, test, and deploy your application based on a predefined CI/CD configuration.Learn more in the Auto DevOps documentation
        Please retype the email address.
        previous fire time
        1.1版本代码修改提交测试
    """
    quartz = Quartz()
    quartz.start()
