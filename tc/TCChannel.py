#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import re
import random
import json
import time
import threading
sys.path.append('../base')
import Common as Common
import Config as Config
from TCCrawler import TCCrawler
from RetryCrawler import RetryCrawler

class Channel():
    '''A class of TC channel'''
    def __init__(self):
        # 抓取设置
        self.crawler            = TCCrawler()
        self.retrycrawler       = RetryCrawler()
        self.crawling_time      = Common.now() # 当前爬取时间
        self.crawling_time_s    = Common.time_s(self.crawling_time)
        self.crawling_begintime = '' # 本次抓取开始时间
        self.crawling_beginDate = '' # 本次爬取日期
        self.crawling_beginHour = '' # 本次爬取小时

        # 频道信息
        self.platform           = '同程-pc' # 品牌团所在平台
        self.channel_id         = '' # 频道id
        self.channel_url        = '' # 频道链接
        self.channel_name       = '' # 频道name
        self.channel_type       = '' # 频道类型

        # 原数据信息
        self.channel_page       = '' # 频道页面html内容
        self.channel_pages      = {} # 频道页面内请求数据列表

        # channel items
        self.channel_items      = []

        # channel list
        self.channel_list       = []

    # 频道页初始化
    def init(self, channel_id, channel_url, channel_type, begin_time):
        self.channel_id = channel_id
        self.channel_url = channel_url
        self.channel_type = channel_type
        self.crawling_begintime = begin_time
        self.crawling_beginDate = time.strftime("%Y-%m-%d", time.localtime(self.crawling_begintime))
        self.crawling_beginHour = time.strftime("%H", time.localtime(self.crawling_begintime))

    def config(self):
        self.channelPage()
        if self.channel_type == 1:
            self.spot()
        #elif self.channel_type == 2:
        else:
            Common.log('# not find this channel type...')

    def spot(self):
        if self.channel_page:
            m = re.search(r'<title>(.+?)</title>', self.channel_page, flags=re.S)
            if m:
                self.channel_name = m.group(1)

            keyword, pid, cid, cyid = '', 0, 0, 0
            m = re.search(r'<span id="hdKeyWord">(.*?)</span>', self.channel_page, flags=re.S)
            if m:
                keyword = m.group(1)
            m = re.search(r'<span id="hdPid">(.*?)</span>', self.channel_page, flags=re.S)
            if m:
                pid = int(m.group(1))
            m = re.search(r'<span id="hdCid">(.*?)</span>', self.channel_page, flags=re.S)
            if m:
                cid = int(m.group(1))
            m = re.search(r'<span id="hdCyid">(.*?)</span>', self.channel_page, flags=re.S)
            if m:
                cyid = int(m.group(1))
        
            i_p = 1
            i_page = 1
            m_page = 1
            page_main = ''
            m = re.search(r'<div class="scenery_main" id="sceneryListInfo">(.+?)<div id="pageNum_box" class="s_pager none">', self.channel_page, flags=re.S)
            if m:
                page_main = m.group(1)
            else:
                page_main = self.channel_page
            
            Common.log(i_page)
            i_p = self.get_items(page_main, i_p)

            m = re.search(r'<input type="hidden" id="txt_AllpageNumber" value="(.+?)">', page_main, flags=re.S)
            if m:
                m_page = int(m.group(1))

            page_url = 'http://www.ly.com/scenery/SearchList.aspx?&action=getlist&page=%d&kw=&pid=%d&cid=%d&cyid=%d&theme=0&grade=0&money=0&sort=0&paytype=0&ismem=0&istuan=0&isnow=0&spType=&isyiyuan=0&lbtypes=&IsNJL=0&classify=0'
            while i_page < m_page:
                i_page += 1
                p_url = page_url % (i_page, pid, cid, cyid)
                Common.log(i_page)
                page = self.retrycrawler.getData(p_url, self.channel_url)
                i_p = self.get_items(page, i_p)

    def get_items(self, page_main, i_p):
        if page_main:
            p = re.compile(r'<div class="scenery_list(.+?)">\s*<div class="s_info"><div class="img_con"><a class="a_img".+?href="(.+?)"><img.+?src="(.+?)".*?></a></div><div class="info_con"><dl class="info_top"><dt><a class="fir_name".+?>(.+?)</a>.+?<span class="s_level">(.*?)</span>.+?<dd class="scenery_area"><span>(.+?)</span>.+?</dl></div></div>', flags=re.S)
            for info in p.finditer(page_main):
                all_info, i_info, i_url, i_img, i_name, i_level, i_area = info.group(), info.group(1), (Config.tc_home + info.group(2)), info.group(3), info.group(4), re.sub(r'<.+?>', '', info.group(5)), ' '.join(info.group(6).split())
                i_book = 1
                i_desc = ''
                m = re.search(r'<dd class="scenery_desc"><p>(.+?)</p>', all_info, flags=re.S)
                if m:
                    i_desc = m.group(1)
                if i_info.find('nobook') != -1:
                    i_book = 0
                    if i_desc == '':
                        m = re.search(r'<dd class="scenery_state">(.+?)<a', all_info, flags=re.S)
                        if m:
                            i_desc = m.group(1)
                i_id = 0
                if i_url != '':
                    m = re.search(r'BookSceneryTicket_(\d+).html', i_url)
                    if m:
                        i_id = m.group(1)
                    val = (self.channel_id, self.channel_name, self.channel_url, self.channel_type, (i_book, i_id, i_url, i_img, i_name, i_desc, i_level, i_area, i_p, self.crawling_begintime))
                    self.channel_items.append(val)
                #if i_p == 1: Common.log(val)
                i_p += 1
        return i_p

    def channelList(self):
        self.channelPage()
        if self.channel_page:
            city_list = self.moreCity(self.channel_page, 'city')
            for city in city_list:
                city_url, city_name, province_id, city_id, dcity_id = city 
                if city_url:
                    province_name, city_name = '', ''
                    city_page = self.crawler.getData(city_url, self.channel_url)
                    if city_page:
                        m = re.search(r'<div class="search_screen_dl"><dl action="province">.+?<div class="right"><a href=".+?" class="current" tvalue="(\d+)" title="(.+?)">', city_page, flags=re.S)
                        if m:
                            province_id, province_name = m.group(1), m.group(2)
                        m = re.search(r'<div class="search_screen_dl">.+?<dl action="city">.+?<div class="right"><a href=".+?" class="current" tvalue="(\d+)" title="(.+?)">', city_page, flags=re.S)
                        if m:
                            city_id, city_name = m.group(1), m.group(2)
                    channel_list = self.moreCity(city_page, 'district')
                    if channel_list and len(channel_list) > 0:
                        for channel in channel_list:
                            channel_url, channel_name, p_id, c_id, cy_id = channel
                            self.channel_list.append((str(cy_id), channel_name, channel_url, str(self.channel_type), city_id, city_name, province_id, province_name))

    def moreCity(self, page, action_key):
        city_list = []
        if page:
            p_id, c_id, cy_id = 0, 0, 0
            m = re.search(r'<span id="hdPid">(.*?)</span>', page, flags=re.S)
            if m:
                p_id = int(m.group(1))
            m = re.search(r'<span id="hdCid">(.*?)</span>', page, flags=re.S)
            if m:
                c_id = int(m.group(1))
            m = re.search(r'<span id="hdCyid">(.*?)</span>', page, flags=re.S)
            if m:
                cy_id = int(m.group(1))
            
            p_url = 'http://www.ly.com/scenery/scenerysearchlist_%d_%d__0_0_0_%d_0_0_0.html'
            m = re.search(r'<div class="search_screen_box" id="searchScreenBox">.+?<dl action="%s".+?>.+?<dd>.+?<div class="right">(.+?)</div></dd>' % action_key, page, flags=re.S)
            if m:
                city_infos = m.group(1)
                p = re.compile(r'<a.+?tvalue="(\d+)" title="(.+?)">', flags=re.S)
                for city in p.finditer(city_infos):
                    city_id, city_name = int(city.group(1)), city.group(2)
                    if action_key == 'city':
                        c_id = city_id
                    elif action_key == 'district':
                        cy_id = city_id
                    city_url, city_name = p_url % (p_id, c_id, cy_id), city.group(2)
                    city_list.append((city_url, city_name, p_id, c_id, cy_id))
        return city_list

    def channelPage(self):
        if self.channel_url:
            data = self.crawler.getData(self.channel_url, Config.tc_home)
            if not data and data == '': raise Common.InvalidPageException("# channelPage:not find channel page,channel_id:%s,channel_url:%s"%(str(self.channel_id), self.channel_url))
            if data and data != '':
                self.channel_page = data
                self.channel_pages['channel-home'] = (self.channel_url, data)


    def antPage(self, val):
        channel_id, channel_url, channel_type, begin_time = val
        self.init(channel_id, channel_url, channel_type, begin_time)
        self.config()

    def antChannelList(self, val):
        self.channel_url, self.channel_type = val
        self.channelList()

if __name__ == '__main__':
    Common.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    c = Channel()
    #val = (1, 'http://www.ly.com/scenery/scenerysearchlist_22_295__0_0_0_0_0_0_0.html', 1, Common.now())
    #c.antPage(val)
    val = ('http://www.ly.com/scenery/scenerysearchlist_22_0__0_0_0_0_0_0_0.html', 1)
    c.antChannelList(val)
    for val in c.channel_list:
        Common.log(val)
    time.sleep(1)
    Common.log(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

