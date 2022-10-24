#  -*- coding: utf-8 -*-
# @Time:2022/10/23   6:07
# @Author: Lanser
# @File:kugou.py
# Software:PyCharm
# 获取酷狗繁星直播的真实流媒体地址，默认最高码率。

import requests
import sys
# sys.path.insert(0, '..')
from .requests_code import requests_get_code
from multiprocessing.pool import ThreadPool

class KuGou:

    def __init__(self, rid):
        """
        酷狗繁星直播
        Args:
            rid: 房间号
        """
        self.rid = rid
        self.s = requests.Session()
        self.url = 'https://fx1.service.kugou.com/video/mo/live/pull/h5/v3/streamaddr'

    def get_real_url(self):
        params = {
            'roomId': self.rid,
            'platform': 18,
            'version': 1000,
            'streamType': '3-6',
            'liveType': 1,
            'ch': 'fx',
            'ua': 'fx-mobile-h5',
            'kugouId': 0,
            'layout': 1
        }
        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}
        try:
            res = self.s.get(self.url, params=params, timeout=2).json()
            if res['code'] == 1:
                return {}
            try:
                real_data_horizontal = res['data']['horizontal']
                real_data_vertical = res['data']['vertical']
                if real_data_horizontal:
                    real_lists.append({'hls': real_data_horizontal[0]['hls'][0]})
                    real_lists.append({'hls': real_data_horizontal[0]['httpshls'][0]})
                if real_data_vertical:
                    real_lists.append({'hls': real_data_vertical[0]['hls'][0]})
                    real_lists.append({'httpshls': real_data_vertical[0]['httpshls'][0]})
            except:
                return {}
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
                    real_dict['kugou'] = real_list
                    return real_dict
            return {}
        except IndexError:
            try:
                url = f'https://fx1.service.kugou.com/biz/ChannelVServices/' \
                      f'RoomLiveService.RoomLiveService.getCurrentLiveStarForMob/{self.rid}'
                res = self.s.get(url).json()
                if res['code'] == 1:
                    return {}
                roomid = res['data']['roomId']
                self.url = 'https://fx2.service.kugou.com/video/pc/live/pull/mutiline/streamaddr'
                params = {
                    'std_rid': roomid,
                    'version': '1.0',
                    'streamType': '1-2-3-5-6',
                    'targetLiveTypes': '1-4-5-6',
                    'ua': 'fx-h5'
                }
                res = self.s.get(self.url, params=params, timeout=2).json()
                real_url = res.get('data').get('lines')[-1].get('streamProfiles')[-1]['httpsHls'][-1]
                real_dict['kugou'] = [{'hls': real_url}, {'rid': self.rid}]
                return real_dict
            except:
                return {}


# if __name__ == '__main__':
#     rid = '6738148'
#     # rid = '2678075'
#     kugou = KuGou(rid)
#     print(kugou.get_real_url())
