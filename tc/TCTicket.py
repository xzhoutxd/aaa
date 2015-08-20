#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
import traceback
import threading
import hashlib
sys.path.append('../base')
import Common as Common
import Config as Config
from TCCrawler import TCCrawler

class Ticket():
    '''A class of tc Ticket'''
    def __init__(self):
        # 商品页面抓取设置
        self.crawler            = TCCrawler()
        self.crawling_time      = Common.now() # 当前爬取时间
        self.crawling_begintime = '' # 本次抓取开始时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时

        # 门票所属商品信息
        self.item_id            = '' # 商品Id
        self.item_name          = '' # 商品Name
        self.item_type          = '' # 商品类型

        # 门票类型
        self.consumer_type        = '' # 门票类型
        self.consumer_type_name   = '' # 门票类型名称

        # 门票信息
        self.ticket_id          = '' # 门票id
        self.ticket_name        = '' # 门票名称
        self.ticket_price       = '' # 门票价
        self.ticket_adprice     = '' # 门票活动价
        self.ticket_dis_adprice = '' # 门票打折活动价
        self.ticket_unit        = '' # 门票
        self.ticket_unit_name   = '' # 门票(套票 单票 套餐等信息)
        self.ticket_tag         = '' # 门票特点
        self.ticket_consumer    = '' # 门票使用人
        self.ticket_contained   = '' # 门票包含项目
        self.ticket_maintitle   = '' # 门票详细说明

        # 数据信息
        self.ticket_pages       = {}


    def ticketConfig(self, t_data):
        if t_data:
            if t_data.has_key('TicketTypeId'):
                if t_data['TicketTypeId'] and int(t_data['TicketTypeId']) != 0:
                    self.ticket_id = t_data['TicketTypeId']
            if t_data.has_key('TicketName') and t_data['TicketName']:
                self.ticket_name = t_data['TicketName']
            if t_data.has_key('Amount') and t_data['Amount']:
                self.ticket_price = t_data['Amount']
            if t_data.has_key('AmountAdvice') and t_data['AmountAdvice']:
                self.ticket_adprice = t_data['AmountAdvice']
            if t_data.has_key('DAmountAdvice') and t_data['DAmountAdvice']:
                self.ticket_dis_adprice = t_data['DAmountAdvice']
            if t_data.has_key('ProductUnit') and t_data['ProductUnit']:
                self.ticket_unit = t_data['ProductUnit']
            if t_data.has_key('ProductUnitName') and t_data['ProductUnitName']:
                self.ticket_unit_name = t_data['ProductUnitName']
            if t_data.has_key('TicketTagEntityList') and t_data['TicketTagEntityList']:
                tags = []
                for tag in t_data['TicketTagEntityList']:
                    if tag.has_key('Name'):
                        tags.append(tag['Name'])
                self.ticket_tag = ';'.join(tags)
            if t_data.has_key('Consumers') and t_data['Consumers']:
                self.ticket_consumer = t_data['Consumers']
            if t_data.has_key('ContainedItems') and t_data['ContainedItems']:
                self.ticket_contained = t_data['ContainedItems']
            if t_data.has_key('MainTitle') and t_data['MainTitle']:
                self.ticket_maintitle = t_data['MainTitle']

            self.ticket_pages['item-init'] = ('', t_data)


    def antPage(self, val):
        self.item_id, self.item_name, self.item_type, self.consumer_type, self.consumer_type_name, self.ticket_id, t_data, self.crawling_begintime = val
        # 本次抓取开始日期
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        # 本次抓取开始小时
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))
        self.ticketConfig(t_data)
        

    def outTuple(self):
        return (self.item_id, self.item_name, self.item_type, self.consumer_type, self.consumer_type_name, self.ticket_id, self.ticket_name, self.ticket_price, self.ticket_adprice, self.ticket_dis_adprice, self.ticket_unit, self.ticket_unit_name, self.ticket_tag, self.ticket_consumer, self.ticket_contained, self.ticket_maintitle, self.crawling_beginDate, self.crawling_beginHour)

    def outSql(self):
        return (Common.time_s(float(self.crawling_time)), self.item_id, self.item_name, self.consumer_type, self.consumer_type_name, self.ticket_id, self.ticket_name, self.ticket_price, self.ticket_adprice, self.ticket_dis_adprice, self.ticket_unit, self.ticket_unit_name, self.ticket_tag, self.ticket_consumer, self.ticket_contained, self.ticket_maintitle, self.crawling_beginDate, self.crawling_beginHour)
