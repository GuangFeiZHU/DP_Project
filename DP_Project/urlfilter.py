#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: ZhuGuangfei

"""
 自定义url去重，每月的爬取的url不能重复
"""
import pymongo
import time
from scrapy.conf import settings
from utils import get_first_day_of_month


class RepeatUrl:
    def __init__(self):
        # 链接数据库
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[settings['MONGO_DB']]  # 获得数据库的句柄
        self.url_coll = self.db[settings['MONGO_COLL_URL']]

    @classmethod
    def from_settings(cls, settings):
        """
        初始化时，调用
        :param settings:
        :return:
        """
        return cls()

    def request_seen(self, request):
        """
        检测当前请求是否已经被访问过
        :param request:
        :return: True表示已经访问过；False表示未访问过
        """
        # if request.url.endswith('/food'):
        #     return False
        filter_dict = {'url': request.url, 'update_time': {'$gte': get_first_day_of_month(),
                                                           '$lte': get_first_day_of_month() + 30 * 24 * 60 * 60}}
        res = self.url_coll.find_one(filter_dict)
        if res:
            return True
        url_info = {'url': request.url, 'update_time': time.time()}
        self.url_coll.update(filter_dict, {'$set': url_info}, upsert=True)
        return False

    def open(self):
        """
        开始爬去请求时，调用
        :return:
        """
        print('open replication')

    def close(self, reason):
        """
        结束爬虫爬取时，调用
        :param reason:
        :return:
        """
        print('close replication')

    def log(self, request, spider):
        """
        记录日志
        :param request:
        :param spider:
        :return:
        """
        print('repeat', request.url)
