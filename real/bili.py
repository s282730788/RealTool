#  -*- coding: utf-8 -*-
# @Time:2022/10/14   0:35
# @Author: Lanser
# @File:bili.py
# Software:PyCharm

# 获取哔哩哔哩直播的真实流媒体地址，默认获取直播间提供的最高画质
# qn=1500高清
# qn=2500超清
# qn=4000蓝光
# qn=10000原画
import requests
import re
import sys
# sys.path.insert(0, '..')
from .requests_code import requests_get_code
from multiprocessing.pool import ThreadPool


class BiliBili:

    def __init__(self, rid):
        """
        有些地址无法在PotPlayer播放，建议换个播放器试试
        Args:
            rid:
        """
        self.rid = rid
        self.header = {
            'User-Agent': 'Mozilla/5.0 (iPod; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, '
                          'like Gecko) CriOS/87.0.4280.163 Mobile/15E148 Safari/604.1',
        }

    def get_real_url(self):
        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init'
        param = {
            'id': self.rid
        }
        with requests.Session() as self.s:
            res = self.s.get(r_url, headers=self.header, params=param, timeout=2).json()
        if '不存在' in res['msg']:
            return {}
        live_status = res['data']['live_status']
        if live_status != 1:
            return {}
        self.real_room_id = res['data']['room_id']
        url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
        param = {
            'room_id': self.real_room_id,
            'protocol': '0,1',
            'format': '0,1,2',
            'codec': '0,1',
            'qn': 10000,
            'platform': 'web',
            'ptype': 8,
        }
        res = self.s.get(url, headers=self.header, params=param, timeout=2).json()
        uid = res['data']['uid']
        stream_info = res['data']['playurl_info']['playurl']['stream']
        accept_qn = stream_info[0]['format'][0]['codec'][0]['accept_qn']
        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}

        for data in stream_info:
            format_name = data['format'][0]['format_name']
            if format_name == 'ts':
                base_url = data['format'][-1]['codec'][0]['base_url']
                url_info = data['format'][-1]['codec'][0]['url_info']
                for i, info in enumerate(url_info):
                    for qn in accept_qn:
                        url_ = base_url
                        host = info['host']
                        extra = info['extra']
                        if qn < 10000:
                            qn = qn * 10
                            url_ = re.sub('bluray/index', f'{qn}/index', base_url)
                        elif qn > 10000:
                            continue

                        extra = re.sub('qn=(\d+)', f'qn={qn}', extra)
                        real_lists.append({f'线路{i + 1}_{qn}': f'{host}{url_}{extra}'})
                break
        if real_lists:
            pool = ThreadPool(processes=int(len(real_lists)))
            for real_ in real_lists:
                thread_list.append(pool.apply_async(requests_get_code, args=(real_,)))
            for thread in thread_list:
                return_dict = thread.get()
                if return_dict:
                    real_list.append(return_dict)
            if real_list:
                real_list.append({'name': self.name(uid)})
                real_list.append({'rid': self.rid})

                real_dict['bili'] = real_list
            if real_dict:
                return real_dict
        return {}

    def name(self, uid):
        url = 'https://api.bilibili.com/x/space/acc/info?mid={}&token=&platform=web&jsonp=jsonp'.format(uid)
        headers = {
            'origin': 'https://space.bilibili.com',
            'referer': 'https://space.bilibili.com/{}/'.format(uid),
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        }
        response = requests.get(url, headers=headers, timeout=1).json()
        name = response['data']['name']
        if response:
            return name
        else:
            return uid
# if __name__ == '__main__':
#     rid = '6'
#     bili = BiliBili(rid)
#     print(bili.get_real_url())
