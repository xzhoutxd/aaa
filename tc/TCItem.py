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
from TCTicket import Ticket

class Item():
    '''A class of tc Item'''
    def __init__(self):
        # 商品页面抓取设置
        self.crawler            = TCCrawler()
        self.crawling_time      = Common.now() # 当前爬取时间
        self.crawling_begintime = '' # 本次抓取开始时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时

        # 单品类型商品所属频道
        self.channel_id         = ''
        self.channel_name       = ''
        self.channel_url        = ''
        self.channel_type       = ''
        self.item_position      = 0

        # 商品信息
        self.item_id            = '' # 商品Id
        self.item_url           = '' # 商品链接
        self.item_pic_url       = '' # 商品展示图片链接
        self.item_name          = '' # 商品Name
        self.item_desc          = '' # 商品说明
        self.item_book_status   = 1  # 商品是否售卖 0:不售,1:在售
        self.item_level         = '' # 级别
        self.item_area          = '' # 地址
        self.item_service       = '' # 服务
        self.item_comment       = '' # 评论数
        self.item_comment_rate  = '' # 好评率
        self.item_comment_good  = '' # 好评数

        # 商品交易
        self.item_oriprice      = '' # 商品原价
        self.item_disprice      = '' # 商品折扣价
        self.item_discount      = '' # 商品打折

        # 门票
        self.item_tickets       = []

        # 原数据信息
        self.item_pageData      = '' # 商品所属数据项内容
        self.item_page          = '' # 商品页面html内容
        self.item_pages         = {} # 商品页面内请求数据列表


    # 商品页信息
    def spotConfig(self, _val):
        self.item_book_status, self.item_id, self.item_url, self.item_pic_url, self.item_name, self.item_desc, self.item_level, self.item_area, self.item_position, self.crawling_begintime = _val
        # 本次抓取开始日期
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        # 本次抓取开始小时
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))
        if self.item_book_status == 1:
            # 商品页信息
            self.itemPage()
            page = self.item_page
            self.item_pages['item-home'] = (self.item_url, self.item_page)

            m = re.search(r'<div class="s-ppp">\s*<div class="s-tp">(.+?)</div>', page, flags=re.S)
            if m:
                i_disprice = re.sub(r'<.+?>', '', m.group(1))
                m = re.search(r'(\d+)', i_disprice)
                if m:
                    self.item_disprice = m.group(1)
                else:
                    self.item_disprice = Common.htmlDecode(i_disprice)
            m = re.search(r'<div class="s-ppp">.+?<div class="s-mp"><s>(.+?)</s>\s+<span>(.+?)</span>', page, flags=re.S)
            if m:
                i_oriprice, i_discount = m.group(1), m.group(2)
                m = re.search(r'(\d+)', i_oriprice)
                if m:
                    self.item_oriprice = m.group(1)
                else:
                    self.item_oriprice = Common.htmlDecode(i_oriprice)
                m = re.search(r'(\d+\.\d+)', i_discount)
                if m:
                    self.item_discount = m.group(1)
                else:
                    m = re.search(r'(\d+)', i_discount)
                    if m:
                        self.item_discount = m.group(1)
                    else:
                        self.item_discount = i_discount

            m = re.search(r'<div class="s-sr">\s+<span.+?>(.+?)</div>', page, flags=re.S)
            if m:
                self.item_service = re.sub(r'<.+?>', '', ';'.join(m.group(1).split()))

            self.itemComment()
    
            self.itemTicket()

    def itemComment(self):
        c_url = 'http://tctj.ly.com/jrec/wlfrec?_dAjax=callback&cid=105&userId=1001&rid=%d&projectId=3&type=1&flag=2&pageSize=10&page=1&callback=tc%s' % (int(self.item_id), Common.rand_n(11))
        #c_url = 'http://tctj.ly.com/jrec/wlfrec?cid=105&userId=1001&rid=%d&projectId=3&type=0&flag=1&pageSize=10&page=1&_dAjax=callback&callback=tc%s' % (int(self.item_id), Common.rand_n(11))
        c_page = self.crawler.getData(c_url, self.item_url)
        
        if c_page:
            m = re.search(r'"count":.+?"all":"(\d+)"', c_page, flags=re.S)
            if m:
                self.item_comment = m.group(1)
            m = re.search(r'"count":.+?"satisfaction":"(.+?)"', c_page, flags=re.S)
            if m:
                self.item_comment_rate = m.group(1)
            m = re.search(r'"count":.+?"good":"(\d+)"', c_page, flags=re.S)
            if m:
                self.item_comment_good = m.group(1)

    def itemTicket(self):
        t_url = 'http://www.ly.com/scenery/AjaxHelper/SceneryPriceFrame.aspx?action=GETNEWPRICEFRAMEFORLAST&ids=%d&isSimple=1&isShowAppThree=0&widthtype=1&isGrap=1&nobookid=&isyry=1&YpState=1&lon=null&lat=null' % int(self.item_id)
        result = self.crawler.getData(t_url, self.item_url)
        if result:
            try:
                scenery = json.loads(result)
                if scenery.has_key('SceneryPrices'):
                    scenery_list = scenery['SceneryPrices']
                    for destination in scenery_list:
                        if destination.has_key('DestinationId') and int(destination['DestinationId']) == int(self.item_id):
                            if destination.has_key('ChannelPriceModelEntityList'):
                                for pricemodel in destination['ChannelPriceModelEntityList']:
                                    if pricemodel.has_key('ConsumersTypeId') and pricemodel.has_key('ConsumersTypeName') and pricemodel.has_key('ChannelPriceEntityList'):
                                        consumer_type = pricemodel['ConsumersTypeId']
                                        consumer_type_name = pricemodel['ConsumersTypeName']
                                        
                                        t_i = 1
                                        for t_data in pricemodel['ChannelPriceEntityList']:
                                            val = (self.item_id, self.item_name, self.channel_type, consumer_type, consumer_type_name, t_i, t_data, self.crawling_begintime)
                                            t = Ticket()
                                            t.antPage(val)
                                            self.item_tickets.append(t.outSql())
                                            t_i += 1
                                    
            except Exception as e:
                Common.log('# itemTicket,exception err in load json: %s' % e)
                Common.traceback_log()


    # 商品详情页html
    def itemPage(self):
        if self.item_url != '':
            refer_url = self.channel_url
            page = self.crawler.getData(self.item_url, refer_url)

            if type(self.crawler.history) is list and len(self.crawler.history) != 0 and re.search(r'302',str(self.crawler.history[0])):
                if not self.itempage_judge(page):
                    Common.log('#crawler history:')
                    Common.log(self.crawler.history)
                    raise Common.NoPageException("# itemPage: not find item page, redirecting to other page,id:%s,item_url:%s"%(str(self.item_id), self.item_url))

            if not page or page == '':
                Common.log('#crawler history:')
                Common.log(self.crawler.history)
                raise Common.InvalidPageException("# itemPage: find item page empty,id:%s,item_url:%s"%(str(self.item_id), self.item_url))
            self.item_page = page
        else:
            raise Common.NoPageException("# itemPage: not find item page, url is null,id:%s,item_url:%s"%(str(self.item_id), self.item_url))

    # 执行
    def antPage(self, val):
        self.channel_id, self.channel_name, self.channel_url, self.channel_type, i_val = val
        if self.channel_type == 1:
            self.spotConfig(i_val)

    def outTuple(self):
        return (self.channel_id, self.channel_name, self.channel_url, self.channel_type, self.item_position, self.item_book_status, self.item_id, self.item_url, self.item_pic_url, self.item_name, self.item_desc, self.item_level, self.item_area, self.item_service, self.item_comment, self.item_comment_good, self.item_comment_rate, self.item_oriprice, self.item_disprice, self.item_discount, self.crawling_beginDate, self.crawling_beginHour)

    def outSql(self):
        return (Common.time_s(float(self.crawling_time)), str(self.item_id), self.item_name, self.item_desc, self.item_url, self.item_pic_url, str(self.item_book_status), self.item_level, self.item_area, self.item_service, str(self.item_comment), str(self.item_comment_good), self.item_comment_rate, str(self.item_oriprice), str(self.item_disprice), str(self.item_discount), str(self.channel_id), str(self.item_position), self.crawling_beginDate, self.crawling_beginHour)

if __name__ == '__main__':
    Common.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    i = Item()
    val = (1, '\xe5\xa8\x81\xe6\xb5\xb7\xe6\x99\xaf\xe5\x8c\xba\xe9\x97\xa8\xe7\xa5\xa8\xe9\xa2\x84\xe8\xae\xa2_\xe5\xa8\x81\xe6\xb5\xb7\xe6\x97\x85\xe6\xb8\xb8\xe6\x99\xaf\xe7\x82\xb9\xe5\xa4\xa7\xe5\x85\xa8_\xe6\x99\xaf\xe7\x82\xb9\xe9\x97\xa8\xe7\xa5\xa8_\xe5\x90\x8c\xe7\xa8\x8b\xe6\x97\x85\xe6\xb8\xb8', 'http://www.ly.com/scenery/scenerysearchlist_22_295__0_0_0_0_0_0_0.html', 1, (1, '2685', 'http://www.ly.com/scenery/BookSceneryTicket_2685.html', 'http://pic3.40017.cn/scenery/destination/2015/04/18/08/QWjL4W_240x135_00.jpg', '\xe5\x88\x98\xe5\x85\xac\xe5\xb2\x9b', '\xe5\x88\x98\xe5\x85\xac\xe5\xb2\x9b\xe4\xb8\x8d\xe4\xbb\x85\xe4\xbb\x85\xe6\x98\xaf\xe4\xb8\x80\xe5\xba\xa7\xe5\xb2\x9b', 'AAAAA', '\xe5\xb1\xb1\xe4\xb8\x9c\xe7\x9c\x81\xe5\xa8\x81\xe6\xb5\xb7\xe5\xb8\x82\xe5\xa8\x81\xe6\xb5\xb7\xe6\xb9\xbe\xe5\x8f\xa3\xe6\xb5\xb7\xe6\xbb\xa8\xe5\x8c\x97\xe8\xb7\xaf48', 1, Common.now()))

    i.antPage(val)
    i_val = i.outTuple()
    for s in i_val:
        Common.log(s)

    for t in i.item_tickets:
        Common.log(t)
    time.sleep(1)
    Common.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))


