# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.conf import settings
from bs4 import BeautifulSoup
import sys, io, re, time
from selenium import webdriver
from scrapy import signals
from pydispatch import dispatcher
from scrapy.exceptions import CloseSpider
from ..items import ShopInfoItem, CommtentInfoItem

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')
from utils import parse_page, parse_shop_foot, modify_score, modify_comment, modify_time, modify_text_score, \
    get_tomorrow
import win_unicode_console

win_unicode_console.enable()


class DianpingSpider(scrapy.Spider):
    name = 'dianping'
    allowed_domains = ['dianping.com']
    start_urls = ['http://www.dianping.com/chongqing/food']

    def __init__(self):
        self.browser = webdriver.Chrome()
        super(DianpingSpider, self).__init__()
        # 绑定信号量，当spider关闭时调用我们的函数
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.tomorrow = get_tomorrow()
        # self.end_time = time.time() + 5 * 60 * 60
        self.end_time = time.time() + 120 * 60

    def spider_closed(self, spider):
        print('spider closed')
        self.browser.quit()

    # start_urls = ['http://www.dianping.com/shenzhen/food']
    def start_requests(self):
        """
        先请求主页，获取cookie
        :return:
        """

        for url in self.start_urls:
            yield Request(url, callback=self.parse0, dont_filter=True)  # dont_filter是否去重url,True是不去重

    def parse0(self, response):
        """
        随便进入一条美食分类，为了获取进一步的美食分类和地点分类
        :param response:
        :return:
        """
        # 先进行一次登录操作
        self.browser.get(
            url='https://www.dianping.com/account/iframeLogin?callback=EasyLogin_frame_callback0&wide=false&protocol=https:&redir=http%3A%2F%2Fwww.dianping.com%2Fchongqing%2Ffood')
        try:
            change_country_code = 'document.getElementsByClassName("code")[0].innerText="+1"'
            change_country_cn_code = 'document.getElementsByClassName("country")[0].innerText="美国"'
            account = '2722001337'
            password = 'sdfs*89grtrasdf'
            self.browser.find_element_by_class_name('icon-pc').click()
            import time
            time.sleep(3)
            # 发送手机号及密码
            self.browser.find_element_by_class_name('tab-account').click()
            time.sleep(3)
            # 修改 国家代码及国家名称
            self.browser.execute_script(change_country_code)
            self.browser.execute_script(change_country_cn_code)
            time.sleep(3)
            self.browser.find_element_by_id('account-textbox').send_keys(account)
            self.browser.find_element_by_id('password-textbox').send_keys(password)
            self.browser.find_element_by_id('login-button-account').click()
            time.sleep(3)
            # 点击登录
        finally:
            #  self.browser.quit()  #不能退出浏览器
            for url in self.start_urls:
                yield Request(url, callback=self.parse1, dont_filter=True)  # dont_filter是否去重url,True是不去重

    def parse1(self, response):
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        business_area = soup.find('div', attrs={'class': 'f_pop_penel f_pop_business'})
        dishs_types = soup.find('div', attrs={'class': 'f_pop_penel f_pop_cooking'})
        dl_list = business_area.find_all('dl')
        rigin_list = list()
        for dl in dl_list:
            sub_dict = dict()
            dt = dl.find_all('dt')
            # 区的中文名称
            district_cn = dt[0].text
            # 区的代号
            district_code = dt[0].find('a')['href'].split('/')[-1]
            # print(dt[0].text,dt[0].find('a')['href'].split('/')[-1])
            li_list = dl.find_all('li')
            business_list = []
            for li in li_list:
                business_dict = dict()
                business_rigin_cn = li.text.split("|")[0].strip()
                business_rigin_code = li.find('a')['href'].split('/')[-1]
                business_dict['business_rigin_cn'] = business_rigin_cn
                business_dict['business_rigin_code'] = business_rigin_code
                business_list.append(business_dict)
                # print((business_rigin_cn.split("|")[0]).strip(),li.find('a')['href'].split('/')[-1])
            sub_dict['district_cn'] = district_cn
            sub_dict['district_code'] = district_code
            sub_dict['business_list'] = business_list
            rigin_list.append(sub_dict)
        dl_list_cooking = dishs_types.find_all('a')
        dish_data_list = list()
        for a_tag in dl_list_cooking:
            sub_dict = dict()
            dish_cn = a_tag.text
            dish_code = a_tag['href'].split('/')[-1]
            sub_dict['dish_cn'] = dish_cn
            sub_dict['dish_code'] = dish_code
            dish_data_list.append(sub_dict)
            # {'business_list': [{'business_rigin_code': 'r8356', 'business_rigin_cn': '坪山'}], 'district_cn': '坪山区', 'district_code': 'r12035'}
        # for item in dish_data_list:
        #     print('dish_data_list item', item)
        # 尝试解析第一个组合页面 http://www.dianping.com/shenzhen/ch10/g117r6013  菜品分类+商区分类
        flag = False
        for dish_type in dish_data_list:
            if flag:
                break
            for rigin_type in rigin_list:
                if flag:
                    break
                for district in rigin_type['business_list']:
                    url = '/'.join(self.start_urls[0].split('/')[:-1]) + '/ch10/' + dish_type['dish_code'] + district[
                        'business_rigin_code']
                    print('----url ', url)
                    yield Request(url, callback=self.parse_shops, dont_filter=False, headers={'Referer': response.url})
                    # 爬虫在凌晨五点开始结束运行
                    if time.time() > self.end_time:
                        print('----get combine of place and dishes done by time ----------------------')
                        self.logger.info(
                            '----get combine of place and dishes done by time --time %s--------------------' % time.time())
                        flag = True
                        break

    def parse_shops(self, response):
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        shops_list = parse_page(soup)
        for shop in shops_list:
            # 爬取单个店铺
            yield Request(shop['shop_url'], callback=self.parse_shop, dont_filter=False)

        foot_url_list = parse_shop_foot(soup)
        for foot_url in foot_url_list:
            yield Request(foot_url, callback=self.parse_other_shops, dont_filter=False,
                          headers={'Referer': response.url})

    def parse_shop(self, response):
        """
        爬取单个商铺的信息
        # http://www.dianping.com/shop/91037021
        :param response:
        :return:
        """
        if response.status == 403:
            raise CloseSpider('403 status shows --')
        shop_item = ShopInfoItem()
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        shop_dict = dict()
        # 获取商铺基本信息
        shop_meta = soup.find('div', attrs={'class': 'breadcrumb'})
        shop_meta_atag = shop_meta.find_all('a')
        if shop_meta and shop_meta_atag:
            try:
                city_name = shop_meta_atag[0].text
                city_code = shop_meta_atag[0]['href'].split('/')[-2]
                dish_type_cn = shop_meta_atag[1].text
                dish_type_code = shop_meta_atag[1]['href'].split('/')[-1]
                district_name = shop_meta_atag[2].text
                district_code = shop_meta_atag[2]['href'].split('/')[-1]
                rigin_name = shop_meta_atag[3].text
                rigin_code = shop_meta_atag[3]['href'].split('/')[-1]
            except Exception as e:
                self.logger.error('error:%s' % str(e))
                city_name = '重庆美食'
                city_code = "chongqing"
                dish_type_cn = shop_meta_atag[1].text
                dish_type_code = shop_meta_atag[1]['href'].split('/')[-1]
                rigin_name = shop_meta_atag[0].text
                rigin_code = shop_meta_atag[0]['href'].split('/')[-2]
                district_name = shop_meta_atag[2].text
                district_code = shop_meta_atag[2]['href'].split('/')[-1]

            shop_dict['city_name'] = city_name
            shop_dict['city_code'] = city_code
            shop_dict['dish_type_cn'] = dish_type_cn
            shop_dict['dish_type_code'] = dish_type_code
            shop_dict['district_name'] = district_name
            shop_dict['district_code'] = district_code
            shop_dict['rigin_name'] = rigin_name
            shop_dict['rigin_code'] = rigin_code

        shop_name_span = shop_meta.find('span')
        if shop_name_span:
            shop_name = shop_name_span.text
            shop_dict['shop_name'] = shop_name
        # 获取商铺环境评论等信息
        shop_bref_info = soup.find('div', attrs={'class': 'brief-info'})
        if shop_bref_info:
            rank = shop_bref_info.find('span', attrs={'class': 'mid-rank-stars'})

            shop_rank_cn = rank['title']

            shop_rank_score = re.findall(r'\d+', rank['class'][-1])[0]
            shop_dict['shop_rank_score'] = shop_rank_score
            shop_dict['shop_rank_cn'] = shop_rank_cn
            other_span_items = shop_bref_info.find_all('span', attrs={'class': 'item'})
            if other_span_items:
                shop_comment_num = modify_score(other_span_items[0])
                avg_cost = modify_score(other_span_items[1])
                flavor_score = modify_score(other_span_items[2])
                environment_score = modify_score(other_span_items[3])
                service_score = modify_score(other_span_items[4])

                shop_dict['shop_comment_num'] = shop_comment_num
                shop_dict['avg_cost'] = avg_cost
                shop_dict['flavor_score'] = flavor_score
                shop_dict['environment_score'] = environment_score
                shop_dict['service_score'] = service_score

        # 商铺地址
        street_address = soup.find('span', attrs={'itemprop': 'street-address'})
        if street_address:
            try:
                place = street_address.text
            except Exception as e:
                print('erro while get place%s' % str(e))
                place = ''
            shop_dict['place'] = place

        shop_url = response.request.url  # 用在scrapy框架
        shop_dict['shop_url'] = shop_url
        # ajax 加载的数据暂时没取出
        recommend_dishs = soup.find('div', attrs={'class': 'shop-tab-recommend J-panel'})

        if recommend_dishs:
            recommend_dishs_tags = recommend_dishs.find_all('a', attrs={'class': 'item'})
            if recommend_dishs_tags:
                dishs_list = []
                for a_tag in recommend_dishs_tags:
                    dishs_list.append(a_tag['title'])
                shop_dict['recommend_dishs'] = dishs_list

        shop_story = soup.find('p', attrs={'class': 'J_all'})
        if shop_story:
            shop_story_text = shop_story.text
            shop_dict['shop_story_text'] = shop_story_text
        location_div = soup.find('div', attrs={'id': 'map'})
        if location_div:
            location = location_div.find('img')['src'].split('|')[-1]
            shop_dict['location'] = location

        good_summy = soup.find_all('span', attrs={'class': 'J-summary'})
        if good_summy:
            brief_comments = []
            for good in good_summy:
                if good:
                    good_tag = good.find('a')
                    if good_tag:
                        brief_comments.append(good_tag.text)
            shop_dict['brief_comments'] = brief_comments
        shop_dict['update_time'] = time.time()
        print('shop_dict', shop_dict)
        shop_item['shop_info'] = shop_dict
        yield shop_item
        # 进入爬取店铺评论
        yield Request(url=shop_url + '/review_all', callback=self.parse_comments, dont_filter=False,
                      headers={'Referer': response.url})

    def parse_other_shops(self, response):
        """
        爬取其他分页url上的商铺列表
        #http://www.dianping.com/shenzhen/ch10/g110r28441p2 -->分页
        :param response:
        :return:
        """
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        shops = parse_page(soup)
        for shop in shops:
            # 爬取单个店铺
            yield Request(shop['shop_url'], callback=self.parse_shop, dont_filter=False,
                          headers={'Referer': response.url})

    def parse_comments(self, response):
        """
        爬取商铺评论信息
        :param response:
        :return:
        """
        if response.status == 403:
            raise CloseSpider('403 status shows --')
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        comments_div = soup.find('div', attrs={'class': 'reviews-items'})
        if comments_div:
            li_list = comments_div.find_all('li')
            if li_list:
                for item_ in li_list:
                    # 用户信息
                    item = CommtentInfoItem()
                    shop_commtents = dict()
                    user_info = item_.find('a', attrs={'class', 'name'})

                    if user_info:
                        user_url = user_info['href']
                        user_name = modify_comment(user_info.text)
                        shop_commtents['user_url'] = user_url
                        shop_commtents['user_name'] = user_name

                    user_rank = item_.find('span', attrs={'class': 'user-rank-rst'})
                    if user_rank:
                        user_rank_text = user_rank['class']
                        shop_commtents['user_rank_text'] = modify_text_score(''.join(user_rank_text))

                    # 用户给商铺的点评信息
                    rank = item_.find('span', attrs={'sml-rank-stars'})
                    if rank:
                        rank_score = rank['class']
                        shop_commtents['rank_score'] = modify_text_score(''.join(rank_score))

                    score = item_.find('span', attrs={'class': 'score'})
                    if score:
                        score_items = score.find_all('span', attrs={'class': 'item'})
                        if score_items:
                            score_discrible = [item.text.strip() for item in score_items]
                            shop_commtents['score_discrible'] = score_discrible
                    comment_div = item_.find('div', attrs={'class': 'review-words'})
                    if comment_div:
                        br = comment_div.find_all(text=True)
                        shop_commtents['comment'] = '。'.join([modify_comment(str(item)) for item in br])
                    comment_time = soup.find('span', attrs={'class': 'time'})
                    if shop_commtents:
                        if comment_time:
                            shop_commtents['comment_time'] = modify_time(comment_time.text)
                        shop_url_div = soup.find('div', attrs={'class': 'review-list-header'})
                        if shop_url_div:
                            shop_url_a = shop_url_div.find('a')
                            if shop_url_a:
                                shop_url = 'http://www.dianping.com' + shop_url_a['href']
                                shop_commtents['shop_url'] = shop_url
                        print('shop_comments', shop_commtents)
                        shop_commtents['update_time'] = time.time()
                        item['comment_info'] = shop_commtents
                        yield item
        # 获取分页url:
        last_page_a = soup.find_all('a', attrs={'class': 'PageLink'})
        if last_page_a:
            last_page_num = last_page_a[-1]['title']
            print('--last_page_num---', last_page_num)
            if last_page_num:
                if last_page_num == 2:
                    url_next = response.request.url + '/p2'
                    yield Request(url=url_next, callback=self.parse_other_comments, dont_filter=False)
                else:
                    for i in range(2, int(last_page_num) + 1):
                        url_temp = response.request.url + '/p%s' % i
                        yield Request(url=url_temp, callback=self.parse_other_comments, dont_filter=False,
                                      headers={'Referer': response.url})

    def parse_other_comments(self, response):
        """
        爬取商铺评论信息
        :param response:
        :return:
        """
        # comment_item = CommtentInfoItem()
        if response.status == 403:
            raise CloseSpider('403 status shows --')
        soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
        comments_div = soup.find('div', attrs={'class': 'reviews-items'})
        if comments_div:
            li_list = comments_div.find_all('li')
            if li_list:
                for item_ in li_list:
                    # 用户信息
                    item = CommtentInfoItem()
                    shop_commtents = dict()
                    user_info = item_.find('a', attrs={'class', 'name'})

                    if user_info:
                        user_url = user_info['href']
                        user_name = modify_comment(user_info.text)
                        shop_commtents['user_url'] = user_url
                        shop_commtents['user_name'] = user_name

                    user_rank = item_.find('span', attrs={'class': 'user-rank-rst'})
                    if user_rank:
                        user_rank_text = user_rank['class']
                        shop_commtents['user_rank_text'] = modify_text_score(''.join(user_rank_text))

                    # 用户给商铺的点评信息
                    rank = item_.find('span', attrs={'sml-rank-stars'})
                    if rank:
                        rank_score = rank['class']
                        shop_commtents['rank_score'] = modify_text_score(''.join(rank_score))

                    score = item_.find('span', attrs={'class': 'score'})
                    if score:
                        score_items = score.find_all('span', attrs={'class': 'item'})
                        if score_items:
                            score_discrible = [item.text.strip() for item in score_items]
                            shop_commtents['score_discrible'] = score_discrible
                    comment_div = item_.find('div', attrs={'class': 'review-words'})
                    if comment_div:
                        br = comment_div.find_all(text=True)
                        shop_commtents['comment'] = '。'.join([modify_comment(str(item)) for item in br])
                    comment_time = soup.find('span', attrs={'class': 'time'})
                    if shop_commtents:
                        if comment_time:
                            shop_commtents['comment_time'] = modify_time(comment_time.text)
                        shop_url_div = soup.find('div', attrs={'class': 'review-list-header'})
                        if shop_url_div:
                            shop_url_a = shop_url_div.find('a')
                            if shop_url_a:
                                shop_url = 'http://www.dianping.com' + shop_url_a['href']
                                shop_commtents['shop_url'] = shop_url
                        print('shop_comments', shop_commtents)
                        shop_commtents['update_time'] = time.time()
                        item['comment_info'] = shop_commtents
                        yield item
