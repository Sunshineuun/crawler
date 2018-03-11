#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import logging
import logging.handlers
import sys
import os


def get_defalut_logger(filename, root):
    # 创建log存储目录
    bak_path = os.getcwd() + '\\log'
    if not os.path.exists(bak_path):
        print('创建日志文件夹！')
        os.makedirs('log')

    # 获取logger实例，如果参数为空则返回root logger
    logger = logging.getLogger(root)

    # 指定logger输出格式
    formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')

    # 文件日志
    """
    S-秒，M-分钟，H-小时,D-天，W-周，
    interval 是指等待多少个单位when的时间后，Logger会自动重建文件，当然，这个文件的创建
    取决于filename+suffix，若这个文件跟之前的文件有重名，则会自动覆盖掉以前的文件，所以
    有些情况suffix要定义的不能因为when而重复。
    backupCount 是保留日志个数。默认的0是不会自动删除掉日志。若设3，则在文件的创建过程中
    库会判断是否有超过这个3，若超过，则会从最先创建的开始删除。
    """
    file_handler = logging.handlers.TimedRotatingFileHandler(filename, encoding="UTF-8", when='D', interval=1,
                                                             backupCount=3)
    # 设置后缀名称，跟strftime的格式一样
    file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    # 可以通过setFormatter指定输出格式
    file_handler.setFormatter(formatter)

    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    # 也可以直接给formatter赋值
    console_handler.formatter = formatter

    # 为logger添加的日志处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    '''
    日志级别：
    critical > error > warning > info > debug,notset
    级别越高打印的日志越少，反之亦然，即
    debug    : 打印全部的日志(notset等同于debug)
    info     : 打印info,warning,error,critical级别的日志
    warning  : 打印warning,error,critical级别的日志
    error    : 打印error,critical级别的日志
    critical : 打印critical级别
    '''
    logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.INFO)

    return logger


if __name__ == '__main__':
    logger1 = get_defalut_logger('log/1.log', '1')
    logger2 = get_defalut_logger('log/2.log', '2')
    logger1.debug("debug")
    logger2.debug("bbb")
    logger1.info("info")
