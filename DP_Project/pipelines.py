# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy.conf import settings
from .items import ShopInfoItem, CommtentInfoItem
from utils import get_first_day_of_month


class DpProjectPipeline(object):
    def __init__(self):
        # 链接数据库
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        # 数据库登录需要帐号密码的话
        # self.client.admin.authenticate(settings['MINGO_USER'], settings['MONGO_PSW'])
        self.db = self.client[settings['MONGO_DB']]  # 获得数据库的句柄
        self.shop_coll = self.db[settings['MONGO_COLL_SHOP']]
        self.comment_coll = self.db[settings['MONGO_COLL_COMMENT']]

    def process_item(self, item, spider):
        if isinstance(item, ShopInfoItem):
            shop_info = item['shop_info']
            filter_dict = {'shop_url': shop_info['shop_url'], 'update_time': {'$gte': get_first_day_of_month(),
                                                                              '$lte': get_first_day_of_month() + 30 * 24 * 60 * 60}}
            self.shop_coll.update(filter_dict, {'$set': shop_info}, upsert=True)
        elif isinstance(item, CommtentInfoItem):
            print('item----comment-----------')
            comment_info = item['comment_info']
            filter_dict = {'shop_url': comment_info['shop_url'], 'user_url': comment_info['user_url'],
                           'comment_time': comment_info['comment_time'],
                           'update_time': {'$gte': get_first_day_of_month(),
                                           '$lte': get_first_day_of_month() + 30 * 24 * 60 * 60}}
            self.comment_coll.update(filter_dict, {'$set': comment_info}, upsert=True)
        return item  # 会在控制台输出原item数据，可以选择不写
