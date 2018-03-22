#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie


def str_2_byte(s):
    """
    str to byte
    :param s:
    :return:
    """
    # sb2 = str.encode(s)
    bytes(s, encoding="utf8")


def byte_2_str(b):
    """
    byte to str
    :param b:
    :return:
    """
    # bytes.decode(b)
    str(b, encoding="utf8")


def encode(s):
    """
    转码
    :param s:
    :return:
    """
    return ' '.join([bin(ord(c)).replace('0b', '') for c in s])


def decode(s):
    """
    解码
    :param s:
    :return:
    """
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])
