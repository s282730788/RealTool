#  -*- coding: utf-8 -*-
# @Time:2022/10/23   5:04
# @Author: Lanser
# @File:kuwo.py
# Software:PyCharm

# 酷我聚星直播：http://jx.kuwo.cn/

import requests
import re
import sys
# sys.path.insert(0, '..')
from .requests_code import requests_get_code
from multiprocessing.pool import ThreadPool

class KuWo:

    def __init__(self, rid):
        self.rid = rid
        self.BASE_URL = 'https://jxm0.kuwo.cn/video/mo/live/pull/h5/v3/streamaddr'
        self.s = requests.Session()

    def get_real_url(self):
        res = self.s.get(f'https://jx.kuwo.cn/{self.rid}').text
        roomid = re.search(r"roomId: '(\d*)'", res)
        if roomid:
            self.rid = roomid.group(1)
        else:
            return {}
        params = {
            'std_bid': 1,
            'roomId': self.rid,
            'platform': 405,
            'version': 1000,
            'streamType': '3-6',
            'liveType': 1,
            'ch': 'fx',
            'ua': 'fx-mobile-h5',
            'kugouId': 0,
            'layout': 1,
            'videoAppId': 10011,
        }
        res = self.s.get(self.BASE_URL, params=params, timeout=2).json()
        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}
        if res['data']['sid'] == -1:
            return {}
        try:
            real_url = res['data']['horizontal'][0]['httpshls'][0]
        except (KeyError, IndexError):
            real_url = res['data']['vertical'][0]['httpshls'][0]
        real_lists.append({f'httpshls': real_url})
        if real_lists:
            pool = ThreadPool(processes=int(len(real_lists)))
            for real_ in real_lists:
                thread_list.append(pool.apply_async(requests_get_code, args=(real_,)))
            for thread in thread_list:
                return_dict = thread.get()
                if return_dict:
                    real_list.append(return_dict)
            if real_list:
                real_list.append({'rid': self.rid})
                real_dict['kuwo'] = real_list
                return real_dict
        return {}



# if __name__ == '__main__':
#     r = 'https://x.kuwo.cn/32067302?refer=2193'
#     if 'kuwo.cn' in r:
#         r = re.findall('/(\d+)', r)[0]
#         print(r)
#     kuwo = KuWo(r)
#     print(kuwo.get_real_url())
