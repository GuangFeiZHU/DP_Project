# -*- coding: utf-8 -*-
import scrapy


class BaiduSpider(scrapy.Spider):
    name = 'baidu'
    allowed_domains = ['baidu.com']
    start_urls = ['http://baidu.com/']

    def parse(self, response):
        print('-------')
        filename = response.url.split("/")[-2]
        with open(filename, 'wb') as f:
            print('response',response.text)
            #print('response', response.body.decode('UTF-8'))
            f.write(response.body)
