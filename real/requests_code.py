#  -*- coding: utf-8 -*-
# @Time:2022/10/24   3:21
# @Author: Lanser
# @File:requests_code.py
# Software:PyCharm

import requests

def requests_get_code(real_dict):
    for real_ in real_dict:
        try:
            code = requests.get(real_dict[real_], stream=True, timeout=1).status_code
            if code == 200:
                return real_dict
        except:
            pass
