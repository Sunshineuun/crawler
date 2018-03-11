#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# 二进制转换


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


s1 = '1001101 1101001 1101110 1001110 1101001 1100101 111001 110011 110000 110110 110010 110101'
print(
    encode('github'),
    # decode(encode(s1))
    decode(s1)
)

