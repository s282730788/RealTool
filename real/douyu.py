#  -*- coding: utf-8 -*-
# @Time:2022/10/13   18:34
# @Author: Lanser
# @File:douyu.py
# Software:PyCharm

# 获取斗鱼直播间的真实流媒体地址，默认最高画质
# 使用 https://github.com/wbt5/real-url/issues/185 中两位大佬@wjxgzz @4bbu6j5885o3gpv6ss8找到的的CDN，在此感谢！
import hashlib
import json
import re
import time
import sys
from multiprocessing.pool import ThreadPool
import execjs
import requests

# sys.path.insert(0, '..')
from .requests_code import requests_get_code


class DouYu:
    """
    可用来替换返回链接中的主机部分
    两个阿里的CDN：
    dyscdnali1.douyucdn.cn
    dyscdnali3.douyucdn.cn
    墙外不用带尾巴的akm cdn：
    hls3-akm.douyucdn.cn
    hlsa-akm.douyucdn.cn
    hls1a-akm.douyucdn.cn
    """

    def __init__(self, rid):
        self.rate_list = []
        """
        房间号通常为1~8位纯数字，浏览器地址栏中看到的房间号不一定是真实rid.
        Args:
            rid:
        """
        self.did = '10000000000000000000000000001501'
        self.t10 = str(int(time.time()))
        self.t13 = str(int((time.time() * 1000)))
        self.rid = rid
        self.s = requests.Session()


    @staticmethod
    def md5(data):
        return hashlib.md5(data.encode('utf-8')).hexdigest()

    def get_pre(self):
        url = 'https://playweb.douyucdn.cn/lapi/live/hlsH5Preview/' + self.rid
        data = {
            'rid': self.rid,
            'did': self.did
        }
        auth = DouYu.md5(self.rid + self.t13)
        headers = {
            'rid': self.rid,
            'time': self.t13,
            'auth': auth
        }
        res = self.s.post(url, headers=headers, data=data, timeout=2).json()
        error = res['error']
        data = res['data']
        try:
            for i in res['data']['settings']:
                self.rate_list.append(i)
        except:
            pass
        key = ''
        if data:
            rtmp_live = data['rtmp_live']
            key = re.search(
                r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}(/playlist|.m3u8)', rtmp_live).group(1)
        return error, key

    def get_js(self):
        result = re.search(
            r'(function ub98484234.*)\s(var.*)', self.res).group()
        func_ub9 = re.sub(r'eval.*;}', 'strc;}', result)
        js = execjs.compile(func_ub9)
        res = js.call('ub98484234')

        v = re.search(r'v=(\d+)', res).group(1)
        rb = DouYu.md5(self.rid + self.did + self.t10 + v)

        func_sign = re.sub(r'return rt;}\);?', 'return rt;}', res)
        func_sign = func_sign.replace('(function (', 'function sign(')
        func_sign = func_sign.replace(
            'CryptoJS.MD5(cb).toString()', '"' + rb + '"')

        js = execjs.compile(func_sign)
        params = js.call('sign', self.rid, self.did, self.t10)
        params += '&ver=219032101&rid={}&rate=-1'.format(self.rid)

        url = 'https://m.douyu.com/api/room/ratestream'
        res = self.s.post(url, params=params, timeout=2).text
        json_ = json.loads(res)
        try:
            for i in json_['data']['settings']:
                self.rate_list.append(i)
        except:
            pass
        key = re.search(
            r'(\d{1,8}[0-9a-zA-Z]+)_?\d{0,4}(.m3u8|/playlist)', res).group(1)
        return key

    def get_real_url(self):
        self.res = self.s.get('https://m.douyu.com/' + str(self.rid)).text
        result = re.search(r'rid":(\d{1,8}),"vipId', self.res)

        if result:
            self.rid = result.group(1)
        else:
            return {}
        error, key = self.get_pre()
        if error == 0:
            pass
        elif error == 102:
            return False
        elif error == 104:
            return False
        else:
            key = self.get_js()

        real_lists = []
        real_list = []
        thread_list = []
        real_dict = {}
        if not self.rate_list:
            self.rate_list = [{'name': '蓝光', 'rate': 0, 'high_bit': 1}, {'name': '超清', 'rate': 3, 'high_bit': 0},
                              {'name': '高清', 'rate': 2, 'high_bit': 0}]
        for rate in self.rate_list:
            if rate['rate'] != 0:
                flv = {"{}_flv".format(rate['name']): "http://ws-tct.douyucdn.cn/live/{}_{}.flv?uuid=".format(key, rate[
                    'rate'] * 1000)}
                x_p2p = {"{}_x_p2p".format(rate['name']): "http://ws-tct.douyucdn.cn/live/{}_{}.xs?uuid=".format(key,
                                                                                                                 rate[
                                                                                                                     'rate'] * 1000)}
                aliyun = {
                    "{}_aliyun".format(rate['name']): "http://dyscdnali1.douyucdn.cn/live/{}_{}.flv?uuid=".format(key,
                                                                                                                  rate[
                                                                                                                      'rate'] * 1000)}
                real_lists.append(flv)
                real_lists.append(x_p2p)
                real_lists.append(aliyun)
            else:
                flv = {"{}_flv".format(rate['name']): "http://ws-tct.douyucdn.cn/live/{}.flv?uuid=".format(key)}
                x_p2p = {"{}_x_p2p".format(rate['name']): "http://ws-tct.douyucdn.cn/live/{}.xs?uuid=".format(key)}
                aliyun = {
                    "{}_aliyun".format(rate['name']): "http://dyscdnali1.douyucdn.cn/live/{}.flv?uuid=".format(key)}
                real_lists.append(flv)
                real_lists.append(x_p2p)
                real_lists.append(aliyun)
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
                real_dict['douyu'] = real_list
                return real_dict
        return {}

# if __name__ == '__main__':
#     r = '101'
#     # r = input('输入斗鱼直播间号：\n')
#     s = DouYu(r)
#     print(s.get_real_url())
