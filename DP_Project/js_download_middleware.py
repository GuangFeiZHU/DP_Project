#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: ZhuGuangfei
import scrapy
from scrapy.http import HtmlResponse


class JSPageMiddleware(object):



    # 通过edge请求动态网页，代替scrapy的downloader
    def process_request(self, request, spider):
        # 判断该spider是否为我们的目标
        if spider.browser:
            # browser = webdriver.Edge(
            #     executable_path='F:/PythonProjects/Scrapy_Job/JobSpider/tools/MicrosoftWebDriver.exe')
            spider.browser.get(request.url)
            import time
            time.sleep(5)
            print("访问:{0}".format(request.url))

            # 直接返回给spider，而非再传给downloader
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding="utf-8",
                                request=request)

