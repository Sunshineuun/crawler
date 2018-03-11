#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
import os


# 遍历指定目录，获取目录下的所有文件名
def getDirAllFilePath(dir_path):
    file_path = []
    path_dir = os.listdir(dir_path)
    for all_dir in path_dir:
        child = os.path.join('%s%s' % (dir_path, all_dir))
        file_path.append(child)  # .decode('gbk')是解决中文显示乱码问题
    return file_path


# 读取文件内容并打印
def readFile(file_name):
    """
    文件的全路径
    :param file_name:
    :return:
    """
    content = ''
    file_open = open(file_name, 'r', encoding='utf-8')  # r 代表read
    # for eachLine in file_open:
    #     content += eachLine
    content = file_open.read()
    file_open.close()
    return content


# 输入多行文字，写入指定文件并保存到指定文件夹
def writeFile(file_name, content):
    file_open = open(file_name, 'w')
    file_open.write('%s%s' % (content, os.linesep))
    file_open.close()

