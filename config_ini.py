#  -*- coding: utf-8 -*-
# @Time:2022/10/13   12:00
# @Author: Lanser
# @File:config_ini.py
# Software:PyCharm

from configobj import ConfigObj
import os


def config_():
    config = ConfigObj("%s/config.ini" % os.path.dirname(__file__), encoding='UTF8')
    config['size'] = {}
    config['size']['mul'] = 1
    config['size']['width'] = 438
    config['size']['height'] = 338
    config['background'] = "./image/73114636.png"
    config['quality'] = "all"
    config['font'] = {}
    config['font']['size'] = 26
    config['font']['color'] = '#505050'
    config['real'] = {'douyu': '1', 'bili': '1', 'douyin': '1'}
    config.write()
