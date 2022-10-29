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
import sys
from .requests_code import requests_get_code
from multiprocessing.pool import ThreadPool

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
        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}
        name = ''
        try:
            room_url = 'https://m.huya.com/{}'.format(self.rid)
            header = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/75.0.3770.100 Mobile Safari/537.36 '
            }
            response = requests.get(url=room_url, headers=header, timeout=2).text

            try:
                name = re.findall('"sNick":"(.*?)","iSex"', response)[0]
            except:
                name = self.rid
            liveLineUrl = re.findall(r'"liveLineUrl":"([\s\S]*?)",', response)[0]
            liveline = base64.b64decode(liveLineUrl).decode('utf-8')

            if liveline:
                if 'replay' in liveline:
                    real_lists.append({'直播录像': f'https://{liveline}'})
                else:
                    liveline = self.live(liveline)
                    real_url = ("https:" + liveline).replace("hls", "flv").replace("m3u8", "flv").replace(
                        '&ctype=tars_mobile', '')
                    # rate = re.findall('264_(\d+)', real_url)
                    # if not rate:
                    rate = [500, 2000, 4000, 8000, 10000]

                    for ratio in range(len(rate) - 1, -1, -1):
                        ratio = rate[ratio]

                        if ratio != 10000:
                            real_url_ = real_url.replace('.flv?', f'.flv?ratio={ratio}&')
                            real_lists.append({f'flv_{ratio}': real_url_})
                        else:
                            real_lists.append({f'flv_{ratio}': real_url})
        except:
            pass
        if real_lists:
            pool = ThreadPool(processes=int(len(real_lists)))
            for real_ in real_lists:
                thread_list.append(pool.apply_async(requests_get_code, args=(real_,)))
            for thread in thread_list:
                return_dict = thread.get()
                if return_dict:
                    real_list.append(return_dict)
            if real_list:
                real_list.append({'name': name})
                real_list.append({'rid': self.rid})
                real_dict['huya'] = real_list
            if real_dict:
                return real_dict
        return {}


# rid = input('输入虎牙直播房间号：\n')
# real_url = HuYa(rid)
# print('该直播间源地址为：')
# print(real_url.get_real_url())
