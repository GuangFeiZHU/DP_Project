# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DpProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ShopInfoItem(scrapy.Item):
    """
    商铺数据
    """
    shop_info = scrapy.Field()


class CommtentInfoItem(scrapy.Item):
    """
    评论数据
    """
    comment_info = scrapy.Field()
