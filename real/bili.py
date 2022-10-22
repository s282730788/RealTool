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
        # 先获取直播状态和真实房间号
        r_url = 'https://api.live.bilibili.com/room/v1/Room/room_init'
        param = {
            'id': rid
        }
        with requests.Session() as self.s:
            res = self.s.get(r_url, headers=self.header, params=param, timeout=2).json()
        if res['msg'] == '直播间不存在':
            raise Exception(f'bilibili {rid} {res["msg"]}')
        live_status = res['data']['live_status']
        if live_status != 1:
            raise Exception(f'bilibili {rid} 未开播')
        self.real_room_id = res['data']['room_id']

    def get_real_url(self, current_qn: int = 10000) -> dict:
        url = 'https://api.live.bilibili.com/xlive/web-room/v2/index/getRoomPlayInfo'
        param = {
            'room_id': self.real_room_id,
            'protocol': '0,1',
            'format': '0,1,2',
            'codec': '0,1',
            'qn': current_qn,
            'platform': 'web',
            'ptype': 8,
        }
        res = self.s.get(url, headers=self.header, params=param, timeout=2).json()
        stream_info = res['data']['playurl_info']['playurl']['stream']
        accept_qn = stream_info[0]['format'][0]['codec'][0]['accept_qn']

        bili_dict = {}
        real_list = []
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
                        real_list.append({f'线路{i + 1}_{qn}': f'{host}{url_}{extra}'})
                break

        for real_ in real_list:
            for url_ in real_:
                try:
                    response = requests.get(real_[url_], stream=True, timeout=2)
                    code = response.status_code
                    if code != 200:
                        real_list.remove(real_)
                except:
                    real_list.remove(real_)
        if real_list:
            real_list.append({'rid': self.rid})
            bili_dict['bili'] = real_list
        if bili_dict:
            return bili_dict

# if __name__ == '__main__':
#     rid = '6'
#     bili = BiliBili(rid)
#     print(bili.get_real_url())
