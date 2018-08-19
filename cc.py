#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# Author: ZhuGuangfei
import time
import datetime


# date_time = datetime.date(datetime.date.today().year,datetime.date.today().month,1).timetuple()
# print(time.mktime(date_time))
# print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(1527782400.0)))
def get_first_day_of_month():
    """
    获取本月的第一天 timestamp
    :return:
    """
    date_time = datetime.date(datetime.date.today().year, datetime.date.today().month, 1).timetuple()
    return time.mktime(date_time)

print(get_first_day_of_month())
#
# print(''.join(['1','2']))

# t = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
# print('---',t[:11]+'05:00:00')
#
# now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
# delt = time.mktime(time.strptime(now_time[:8] + '07 05:00:00', '%Y-%m-%d %H:%M:%S')) - time.time()
# print('delt',delt)
# if time.mktime(time.strptime(now_time[:8] + '07 05:00:00', '%Y-%m-%d %H:%M:%S')) - time.time() < 0:
#     print('----------')
#
# # delt = time.mktime(time.strptime(now_time[:8] + '07 05:00:00', '%Y-%m-%d %H:%M:%S')) - time.mktime(
# #         time.strptime(now_time, '%Y-%m-%d %H:%M:%S'))
# print('----get combine of place and dishs done by time --time %s--------------------' % time.time())
def ff():
    flag = False
    for k in range(10):
        if flag:
            print('break--1')
            break
        for j in range(10):
            if flag:
                print('break--2')
                break
            for i in range(10):
                print('i',i)
                yield i
                if i == 3:
                    flag = True
                    break
            print('3 break')
# for i in ff():
#     print('---------')

href="//www.dianping.com/pengshui/food"
print(href.split('/')[-2])

# if time.mktime(time.strptime(self.tomorrow + ' 04:00:00', '%Y-%m-%d %H:%M:%S')) - time.time() < 0:
#     print('----get combine of place and dishes done by time ----------------------')
#     self.logger.info(
#         '----get combine of place and dishes done by time --time %s--------------------' % time.time())
#     flag = True
#     break