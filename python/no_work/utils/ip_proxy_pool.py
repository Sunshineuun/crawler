#!/usr/bin/env python
# encoding: utf-8
# qiushengming-minnie
# IP代理池
import queue


class IPProxyPool(object):

    def __init__(self):
        self._queue = queue.Queue(maxsize=1000)

    def get(self):
        if self._queue.empty():
            # 获取代理IP
            pass

        # 验证


