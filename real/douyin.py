#  -*- coding: utf-8 -*-
# @Time:2022/10/14   22:56
# @Author: Lanser
# @File:douyin.py
# Software:PyCharm

import re
import json
import requests
import urllib.parse
import sys
# sys.path.insert(0, '..')
from .requests_code import requests_get_code
from multiprocessing.pool import ThreadPool


class DouYin:
    def __init__(self, rid):
        self.rid = rid

    def get_real_url(self):

        if 'v.douyin.com' in self.rid:
            self.rid = self.get_room_id(self.rid)
        headers_ = {
            "referer": "https://live.douyin.com/",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0(WindowsNT10.0;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/86.0.4240.198Safari/537.36",
        }
        url = 'https://live.douyin.com/{}'.format(self.rid)
        response_cookies = requests.get(url, headers=headers_).cookies.values()[0]
        headers = {
            "cookie": "__ac_nonce=%s;" % response_cookies,
            "referer": "https://live.douyin.com/",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0(WindowsNT10.0;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/86.0.4240.198Safari/537.36",
        }
        response = requests.get(url, headers=headers).text

        text = urllib.parse.unquote(
            re.findall('<script id="RENDER_DATA" type="application/json">(.*?)</script>', response)[0])
        json_ = json.loads(text)
        try:
            name = json_['app']['initialState']['roomStore']['roomInfo']['room']['owner']['nickname']
        except:
            name = self.rid
        douyin_list = []
        try:
            flv_pull_url = json_['app']['initialState']['roomStore']['roomInfo']['room']['stream_url']['flv_pull_url']
            douyin_list.append(flv_pull_url)
        except:
            pass

        try:
            hls_pull_url_map = json_['app']['initialState']['roomStore']['roomInfo']['room']['stream_url'][
                'hls_pull_url_map']
            douyin_list.append(hls_pull_url_map)
        except:
            pass

        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}

        for real_ in douyin_list:
            for name_ in real_:
                if '.flv' in real_[name_]:
                    real_lists.append({f'flv_{name_}': real_[name_]})
                elif '.m3u8' in real_[name_]:
                    real_lists.append({f'm3u8_{name_}': real_[name_]})

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
                real_dict['douyin'] = real_list
            if real_dict:
                return real_dict
        return {}

    def get_room_id(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        }
        url = re.search(r'(https.*)', url).group(1)
        response = requests.head(url, headers=headers)
        url = response.headers['location']
        room_id = re.search(r'\d{19}', url).group(0)

        headers.update({
            'cookie': '_tea_utm_cache_1128={%22utm_source%22:%22copy%22%2C%22utm_medium%22:%22android%22%2C%22utm_campaign%22:%22client_share%22}',
            'host': 'webcast.amemv.com',
        })
        params = (
            ('type_id', '0'),
            ('live_id', '1'),
            ('room_id', room_id),
            ('app_id', '1128'),
            ('X-Bogus', '1'),
        )

        response = requests.get('https://webcast.amemv.com/webcast/room/reflow/info/?', headers=headers,
                                params=params).json()
        if response:
            return response['data']['room']['owner']['web_rid']
