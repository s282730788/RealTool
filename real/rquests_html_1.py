#  -*- coding: utf-8 -*-
# @Time: 2023/1/15  20:08
# @Author: 须尽欢
# @File: rquests_html_1.py
# @Contact: 282730788@qq.com
# Software: PyCharm

from requests_html import HTMLSession
# import requests
session = HTMLSession()
headers = {
            "cookie": "__ac_nonce=0;",
            "referer": "https://live.douyin.com/",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0(WindowsNT10.0;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/86.0.4240.198Safari/537.36",
        }

# headers = {"Host": "v.douyin.com",
# "Connection": "keep-alive",
# "sec-ch-ua": "Not_A Brand;v=99, Google Chrome;v=109, Chromium;v=109",
# "sec-ch-ua-mobile": "?0",
# "sec-ch-ua-platform": "Windows",
# "Upgrade-Insecure-Requests": "1",
# "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
# "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
# "Sec-Fetch-Site": "none",
# "Sec-Fetch-Mode": "navigate",
# "Sec-Fetch-User": "?1",
# "Sec-Fetch-Dest": "document",
# "Accept-Encoding": "gzip, deflate, br",
#
# "Cookie": "ttwid=1%7Cy7G52XRGM50D_HvVEITMI0Zo9VEqZhMOe9j0lcjJpwI%7C1673787944%7C930453440494f53980e0b938e860106d83e598f8bd3442e85d730260b7441ba0; odin_tt=659faadea0dac0c524a727a98ff51a3b75fe39adc297a932258cf5c5a0663ab61b7b63f59ea7cc540a97c382f7ba7076ccaad5cee4bfdee043ad622d0cb7f003cd2313362989c49c0de1ff7fe715bd1c; msToken=rLEW5ugOkgF6LMV-A0lWKEhIpDDZhk-EpSQbMgGb6n4GIAOnDeVmBBmn6fC80Ktd8xNVyAFOhEYjzsSTRqNBm1g6i08iuYGAqDTg_XXiSO3MmTXlY3w6; live_can_add_dy_2_desktop=%221%22"
# }

url = 'https://v.douyin.com/kQAd2h'

response = session.head(url=url, headers=headers)

print(response.headers)
