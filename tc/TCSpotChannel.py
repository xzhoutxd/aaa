#-*- coding:utf-8 -*-
#!/usr/bin/env python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import random
import json
import time
from TCChannel import Channel
sys.path.append('../base')
import Common as Common
import Config as Config
import Logger as Logger
sys.path.append('../db')
from MysqlAccess import MysqlAccess

class TCSpotChannel():
    '''A class of tc all spot's channels'''
    def __init__(self):
        # DB
        self.mysqlAccess   = MysqlAccess()     # mysql access

        # 页面
        self.site_page  = None

        # 抓取开始时间
        self.begin_time = Common.now()

    def antPage(self):
        try:
            # channel
            c = Channel()
            _val = ('http://www.ly.com/scenery/scenerysearchlist_22_0__0_0_0_0_0_0_0.html', 1)
            c.antChannelList(_val)
            channels = c.channel_list
            if channels and len(channels) > 0:
                Common.log('# add channels num: %d' % len(channels))
                self.mysqlAccess.insertTCChannel(channels)
            else:
                Common.log('# not get channels...')

        except Exception as e:
            Common.log('# TCSpotChannel antpage error: %s'%e)
            Common.traceback_log()

if __name__ == '__main__':
    loggername = 'channel'
    filename = 'add_channel_%s' % (time.strftime("%Y%m%d%H", time.localtime()))
    Logger.config_logging(loggername, filename)
    j = TCSpotChannel()
    Common.log('TCSpotChannel start')
    j.antPage()
    time.sleep(1)
    Common.log('TCSpotChannel end')
