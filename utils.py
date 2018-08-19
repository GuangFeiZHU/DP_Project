#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: ZhuGuangfei

import re
import time
import datetime
from DP_Project.items import CommtentInfoItem


def parse_page(soup):
    """
    获取单个商铺列表页面的所有商铺信息
    http://www.dianping.com/shenzhen/ch10/g110r28441
    :param soup:
    :return:
    """
    # soup = BeautifulSoup(html_text, 'html.parser')
    first_page_shops = soup.find_all('a', attrs={'data-click-name': 'shop_title_click'})
    # 商铺信息的url
    shops = []
    for shop in first_page_shops:
        shop_dict = dict()
        try:
            shop_name = shop['title']
            shop_url = shop['href']
            shop_dict['shop_name'] = shop_name
            shop_dict['shop_url'] = shop_url
            shops.append(shop_dict)
        except Exception as e:
            print('爬取商铺信息出错：%s' % str(e))
            import traceback
            traceback.print_exc()
            continue
    return shops


def parse_shop_foot(soup):
    """
    获取商铺分页列表
    :param soup:
    :return:
    """
    # 获取分页url 列表
    page_links = soup.find_all('a', attrs={'class': 'PageLink'})
    page_links_list = []
    for page in page_links:
        page_link = page['href']
        page_links_list.append(page_link)
    return page_links_list


def modify_score(content):
    """
    正则获取评分等数据
    :param text:
    :return:
    """
    temp = re.findall(r'(\d+(\.\d+)?)', content.text)
    if temp:
        return temp[0][0]
    return None


def modify_text_score(content):
    """
    正则获取评分等数据
    :param text:
    :return:
    """
    temp = re.findall(r'(\d+(\.\d+)?)', content)
    if temp:
        return temp[0][0]
    return None


def modify_comment(content):
    """
    去掉换行符等
    :param text:
    :return:
    """
    temp = re.sub(r'\s+|收起评论+', '', content)
    if temp:
        return temp
    return ''


def modify_time(content):
    """
    去掉换行符等
    :param text:
    :return:
    """
    temp = re.sub(r'\s+', '', content)
    if temp:
        return temp[:10] + ' ' + temp[10:]
    return ''


def parse_comment(soup):
    comment_item = CommtentInfoItem()
    # soup = BeautifulSoup(str(response.body, encoding='utf-8'), 'html.parser')
    comments_div = soup.find('div', attrs={'class': 'reviews-items'})
    if comments_div:
        li_list = comments_div.find_all('li')
        if li_list:
            for item in li_list:
                # 用户信息

                shop_commtents = dict()
                user_info = item.find('a', attrs={'class', 'name'})

                if user_info:
                    user_url = user_info['href']
                    user_name = modify_comment(user_info.text)
                    shop_commtents['user_url'] = user_url
                    shop_commtents['user_name'] = user_name

                user_rank = item.find('span', attrs={'class': 'user-rank-rst'})
                if user_rank:
                    user_rank_text = user_rank['class']
                    shop_commtents['user_rank_text'] = user_rank_text

                # 用户给商铺的点评信息
                rank = item.find('span', attrs={'sml-rank-stars'})
                if rank:
                    rank_score = rank['class']
                    shop_commtents['rank_score'] = rank_score

                score = item.find('span', attrs={'class': 'score'})
                if score:
                    score_items = score.find_all('span', attrs={'class': 'item'})
                    if score_items:
                        score_discrible = [item.text.strip() for item in score_items]
                        shop_commtents['score_discrible'] = score_discrible
                comment_div = item.find('div', attrs={'class': 'review-words'})
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
                            # print('shop_comments', shop_commtents)
                    import time
                    shop_commtents['update_time'] = time.time()
                    comment_item['comment_info'] = shop_commtents
                    yield comment_item


def get_first_day_of_month():
    """
    获取本月的第一天 timestamp
    :return:
    """
    date_time = datetime.date(datetime.date.today().year, datetime.date.today().month, 1).timetuple()
    return time.mktime(date_time)


def get_tomorrow():
    """
    获取明天的日期 2018-07-08
    :return: str
    """
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    return str(tomorrow)
cc = time.mktime(time.strptime(get_tomorrow() + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))-time.time()
print('cc',cc)