#  -*- coding: utf-8 -*-
# @Time:2022/11/2   23:50
# @Author: Lanser
# @File:yizhibo.py
# Software:PyCharm

# 获取一直播的真实流媒体地址。

import requests
import re


class YiZhiBo:

    def __init__(self, rid):
        """
        一直播需要传入直播间的完整地址
        Args:
            rid:完整地址
        """
        self.rid = rid
        self.s = requests.Session()

    def get_real_url(self):
        try:
            url = 'https://www.yizhibo.com/l/{}.html'.format(self.rid)
            real_list = []
            real_dict = {}
            res = self.s.get(url).text
            play_url, name, status_code, memberid = \
                re.findall(r'play_url:"(.*?)"[\s\S]*nickname:"(.*?)"[\s\S]*status:(\d+)[\s\S]*memberid:(.*?),', res)[0]
            if status_code == '10':
                real_list.append({'m3u8': f'{play_url}'})
                real_list.append({'name': f'{name}'})
                real_list.append({'rid': f'{memberid}'})
                real_dict['yizhibo'] = real_list
                return real_dict
            else:
                return {}
        except Exception:
            return {}

