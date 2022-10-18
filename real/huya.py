#  -*- coding: utf-8 -*-
# @Time:2022/10/13   18:34
# @Author: Lanser
# @File:huya.py
# Software:PyCharm

# 获取虎牙直播的真实流媒体地址。

import requests
import re
import base64
import urllib.parse
import hashlib
import time

class HuYa:
    def __init__(self, rid):
        self.rid = rid

    def live(self, e):
        i, b = e.split('?')
        r = i.split('/')
        s = re.sub(r'.(flv|m3u8)', '', r[-1])
        c = b.split('&', 3)
        c = [i for i in c if i != '']
        n = {i.split('=')[0]: i.split('=')[1] for i in c}
        fm = urllib.parse.unquote(n['fm'])
        u = base64.b64decode(fm).decode('utf-8')
        p = u.split('_')[0]
        f = str(int(time.time() * 1e7))
        l = n['wsTime']
        t = '0'
        h = '_'.join([p, t, s, f, l])
        m = hashlib.md5(h.encode('utf-8')).hexdigest()
        y = c[-1]
        url = "{}?wsSecret={}&wsTime={}&u={}&seqid={}&{}".format(i, m, l, t, f, y)
        return url


    def get_real_url(self):
        real_list = []
        try:
            room_url = 'https://m.huya.com/{}'.format(self.rid)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/75.0.3770.100 Mobile Safari/537.36 '
            }
            response = requests.get(url=room_url, headers=header).text
            liveLineUrl = re.findall(r'"liveLineUrl":"([\s\S]*?)",', response)[0]
            liveline = base64.b64decode(liveLineUrl).decode('utf-8')
            if liveline:
                if 'replay' in liveline:
                    return '直播录像：' + liveline
                else:
                    liveline = self.live(liveline)
                    real_url = ("https:" + liveline).replace("hls", "flv").replace("m3u8", "flv")
                    real_url = re.sub('&ctype=tars_mobile', "", real_url)
                    if '.m3u8' in real_url:
                        real_list.append({'m3u8':real_url})
                    elif '.flv' in real_url:
                        real_list.append({'flv': real_url})
        except:
            print('未开播或直播间不存在')

        huya_dict = {}
        if real_list:
            huya_dict['huya'] = real_list
        if huya_dict:
            return huya_dict
