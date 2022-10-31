#  -*- coding: utf-8 -*-
# @Time:2022/9/22   15:40
# @Author: 须尽欢
# @File:RealTool.py
# Software:PyCharm
# Created by: PyQt5 UI code generator 5.14.2
# 直播源项目地址@https://github.com/wbt5/real-url
# m3u8录制工具地址@https://github.com/nilaoda/N_m3u8DL-RE


from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QInputDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QGraphicsDropShadowEffect, QPushButton, QLineEdit, QMessageBox
from PyQt5.Qt import QPropertyAnimation, pyqtSignal, QTranslator, QColorDialog, QFileDialog, QRegExp, QRegExpValidator
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, QThread
import sys
import time
import os
import subprocess
from configobj import ConfigObj
import config_ini
import re
import requests
import ast
from multiprocessing.pool import ThreadPool

from real.douyu import DouYu
from real.huya import HuYa
from real.bili import BiliBili
from real.douyin import DouYin
from real.yy import YY
from real.kuwo import KuWo
from real.kugou import KuGou
from RealListWindow import RealList
from RealRid import RidList


class ThreadGet(QThread):
    _signal = pyqtSignal(dict, str)

    def __init__(self, real_list):
        super(ThreadGet, self).__init__()
        self.real_list = real_list
        self.config = ConfigObj("config.ini", encoding='UTF8')

    def run(self):
        real_dict = {}
        thread_list = []
        pool = ThreadPool(processes=10)
        for rid in self.real_list:
            for real_name_dict in self.config['real']:
                try:
                    if real_name_dict == "douyu" and self.config['real'][real_name_dict] == "1":
                        real_class = DouYu(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "huya" and self.config['real'][real_name_dict] == "1":
                        real_class = HuYa(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "bili" and self.config['real'][real_name_dict] == "1":
                        real_class = BiliBili(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "douyin" and self.config['real'][real_name_dict] == "1":
                        real_class = DouYin(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "yy" and self.config['real'][real_name_dict] == "1":
                        real_class = YY(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "kuwo" and self.config['real'][real_name_dict] == "1":
                        real_class = KuWo(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))

                    if real_name_dict == "kugou" and self.config['real'][real_name_dict] == "1":
                        real_class = KuGou(rid)
                        thread_list.append(pool.apply_async(real_class.get_real_url))
                except Exception as err:
                    print("err:%s" % err)
        for thread in thread_list:
            return_dict = thread.get()
            count = 0
            if return_dict:
                if real_dict:
                    for i in range(len(real_dict)):
                        while list(return_dict.keys())[0] == list(real_dict.keys())[i]:
                            count += 1
                            if f'{list(return_dict.keys())[0].split("_")[0]}_{count}' != list(real_dict.keys())[i]:
                                return_dict.update(
                                    {f'{list(return_dict.keys())[0].split("_")[0]}_{count}': return_dict.pop(
                                        list(return_dict.keys())[0])})
                                break

                real_dict.update(return_dict)
        if real_dict:
            print(real_dict)
            self._signal.emit(real_dict, 'true')
        else:
            self._signal.emit(real_dict, 'false')
        pool.close()


class ButtonGet(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._animation = QtCore.QVariantAnimation(  # 创建一个动画
            startValue=0,
            endValue=100,
            valueChanged=self._on_value_changed,  # 更改值的函数
            duration=400,
        )
        self._update_stylesheet(hover_g_start=200, hover_g_stop=180)

    def _on_value_changed(self, a):  # 更新 改变后的值
        hover_g_start = int(200 + (a / 5))
        hover_g_stop = int(180 + (a / 5))
        self._update_stylesheet(hover_g_start=hover_g_start, hover_g_stop=hover_g_stop)  # 更新并调用样式

    def _update_stylesheet(self, hover_g_start=None, hover_g_stop=None):  # 更新样式函数
        self.setStyleSheet("""
                                                                    QPushButton{                                                                    
                                                                        border-solid: 3px;
                                                                        color:#ffffff;
                                                                        background-color:qlineargradient(
                                                                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                                                                        stop:0 rgba(11,%s,255, 1),
                                                                        stop:1 rgba(0,%s,255, 1));
                                                                        }
                                                                    QPushButton:pressed{
                                                                        background-color:qlineargradient(
                                                                        spread:pad, x1:0, y1:0, x2:0, y2:1,
                                                                        stop:0 rgba(11,190,255, 1),
                                                                        stop:1 rgba(0,185,255, 1));
                                                                        
                                                                    }""" % (hover_g_start, hover_g_stop))

    def enterEvent(self, event):  # 进入
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)  # 正
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):  # 离开
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)  # 反
        self._animation.start()
        super().leaveEvent(event)


class PushButton(QtWidgets.QPushButton):
    def __init__(self, background_img=None, background_color_rgb=None, background_color_rgba=None, duration=None,
                 button_bg=None, pushbutton_stylesheet=None, parent=None):
        """
        :param background_img:图片地址
        :param background_color_rgb:红绿蓝颜色
        :param background_color_rgba:透明度 0~1
        :param duration:持续时间
        :param button_bg:默认背景透明度0~1
        :param pushbutton_stylesheet:其余样式
        :param parent:
        """
        super().__init__(parent)
        self.background_img = background_img
        self.background_color_rgb = background_color_rgb
        self.background_color_rgba = background_color_rgba
        self.button_bg = button_bg
        self.pushbutton_stylesheet = pushbutton_stylesheet

        self._animation = QtCore.QVariantAnimation(  # 创建一个动画
            startValue=0,
            endValue=100,
            valueChanged=self._on_value_changed,  # 更改值的函数
            duration=duration,
        )
        self._update_stylesheet(self.button_bg)

    def _on_value_changed(self, a):  # 更新 改变后的值
        a = a / 100 * self.background_color_rgba + self.button_bg
        self._update_stylesheet(a)  # 更新并调用样式

    def _update_stylesheet(self, a):  # 更新样式函数
        self.setStyleSheet("""QPushButton{
                                background-image: url(%s);
                                background-color:rgba(%s,%s);
                                %s}
                                """ % (self.background_img, self.background_color_rgb, a, self.pushbutton_stylesheet))

    def enterEvent(self, event):  # 进入
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)  # 正
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):  # 离开
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)  # 反
        self._animation.start()
        super().leaveEvent(event)


class ToolButton(QtWidgets.QToolButton):
    def __init__(self, background_img=None, background_color_rgb=None, background_color_rgba=None, duration=None,
                 button_bg=None, pushbutton_stylesheet=None, parent=None):
        """
        :param background_img:图片地址
        :param background_color_rgb:红绿蓝颜色
        :param background_color_rgba:透明度 0~1
        :param duration:持续时间
        :param button_bg:默认背景透明度0~1
        :param pushbutton_stylesheet:其余样式
        :param parent:
        """
        super().__init__(parent)
        self.background_img = background_img
        self.background_color_rgb = background_color_rgb
        self.background_color_rgba = background_color_rgba
        self.button_bg = button_bg
        self.pushbutton_stylesheet = pushbutton_stylesheet

        self._animation = QtCore.QVariantAnimation(  # 创建一个动画
            startValue=0,
            endValue=100,
            valueChanged=self._on_value_changed,  # 更改值的函数
            duration=duration,
        )
        self._update_stylesheet(self.button_bg)

    def _on_value_changed(self, a):  # 更新 改变后的值
        a = a / 100 * self.background_color_rgba + self.button_bg
        self._update_stylesheet(a)  # 更新并调用样式

    def _update_stylesheet(self, a):  # 更新样式函数
        self.setStyleSheet("""QToolButton{
                                                background-image: url(%s);
                                                background-color:rgba(%s,%s);
                                            }
                                            QToolButton::menu-indicator{
                                                image:none;
                                
                                %s}
                                """ % (self.background_img, self.background_color_rgb, a, self.pushbutton_stylesheet))

    def enterEvent(self, event):  # 进入
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)  # 正
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):  # 离开
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)  # 反
        self._animation.start()
        super().leaveEvent(event)


class MainUi(QWidget):
    def __init__(self):
        super(MainUi, self).__init__()
        self.setup_ui()
        self.real_dict = {}
        self.real_id = ''
        self.add_shadow()  # 阴影边框

    def setup_ui(self):

        self.config_ini()
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)  # 隐藏标题栏且可以任务栏最小化
        self.setFixedSize(self.width_, self.height_)
        self.setStyleSheet("""QWidget{
                                                border-radius:3px;
                                                border:none;
                                                }""")
        self.setWindowIcon(QIcon("./image/icon.png"))
        self.setWindowTitle("直播源获取")
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口背景透明
        self.label_background = QLabel(self)  # 创建背景标签
        self.label_background.setGeometry(QtCore.QRect(5, 0, self.width_ - 10, self.height_ - 10))
        self.label_background.setStyleSheet("""QLabel{
                                                                                border:none;
                                                                                background-color:rgba(135,249,255, 1);
                                                                                }""")

        self.label_top_background = QLabel()
        self.label_top_background.setFixedSize(self.width_ - 10, int(self.height_ / 2.7))
        self.label_top_background.setStyleSheet("""QLabel{
                                                                                        border:none;
                                                                                        border-bottom-left-radius:0px;
                                                                                        border-bottom-right-radius:0px;                                                                                        
                                                                                        }""")

        self.label_top_background_image = QLabel(self.label_top_background)
        self.label_top_background_image.setFixedSize(self.width_ - 10, int(self.height_ / 2.7))
        self.label_top_background_image.setStyleSheet("""QLabel{
                                                                                        border:none;
                                                                                        border-bottom-left-radius:0px;
                                                                                        border-bottom-right-radius:0px;
                                                                                        border-image:url('%s');
                                                                                                    }""" % self.config[
            'background'])
        opacity_effect = QtWidgets.QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.85)
        self.label_top_background_image.setGraphicsEffect(opacity_effect)
        self.label_top_background_image.setAutoFillBackground(True)

        self.label_bottom_background = QLabel()
        self.label_bottom_background.setFixedSize(self.label_top_background.width(),
                                                  self.height_ - self.label_top_background.height() - 10)
        self.label_bottom_background.setStyleSheet("""QLabel{
                                                                                            background-color:#ffffff;
                                                                                            border-top-left-radius:0px;
                                                                                            border-top-right-radius:0px;
                                                                                            }""")

        self.label_icon = QLabel(self.label_top_background)
        self.label_icon.setFixedSize(self.label_top_background.width(), 32)
        self.label_icon.setStyleSheet("""QLabel{
                                                                    border:none;
                                                                    border-image:none;                                                                    
                                                                    background-color:rgba(255, 255, 255, 0);                                                               
                                                                    }""")

        self.layout_icon = QtWidgets.QHBoxLayout(self.label_icon)

        self.pushbutton_setting = ToolButton(background_img="./image/setting_icon.png",
                                             background_color_rgb="255,255,255", background_color_rgba=0.2,
                                             duration=200, button_bg=0,
                                             pushbutton_stylesheet="""border:none;background-repeat:no-repeat;width:35px;background-position:center;}QToolButton:pressed{background-color:rgba(255,255,255,0.4);}""")  # 设置按钮样式
        self.pushbutton_setting.setFixedSize(32, 32)
        self.pushbutton_setting.setToolTip("设置")

        self.pushbutton_colse = PushButton(background_img="./image/close_icon.png", background_color_rgb="255,84,57",
                                           background_color_rgba=1, duration=200, button_bg=0,
                                           pushbutton_stylesheet="""border:none;background-repeat:no-repeat;width:32px;background-position:center;}QPushButton:pressed{background-color:rgba(224,74,50,1);}""")  # 关闭按钮样式
        self.pushbutton_colse.setFixedSize(32, 32)
        self.pushbutton_colse.clicked.connect(self.close_)
        self.pushbutton_colse.setToolTip('关闭 Ese')

        self.pushbutton_min = PushButton(background_img="./image/min_icon.png", background_color_rgb="255,255,255",
                                         background_color_rgba=0.2, duration=200, button_bg=0,
                                         pushbutton_stylesheet="""border:none;background-repeat:no-repeat;width:35px;background-position:center;}QPushButton:pressed{background-color:rgba(255,255,255,0.4);}""")  # 最小化按钮样式
        self.pushbutton_min.setFixedSize(32, 32)
        self.pushbutton_min.clicked.connect(self.min_)
        self.pushbutton_min.setToolTip('最小化')

        self.pushbutton_size = PushButton(background_img="./image/size_icon.png", background_color_rgb="255,255,255",
                                          background_color_rgba=0.2, duration=200, button_bg=0,
                                          pushbutton_stylesheet="""border:none;background-repeat:no-repeat;width:35px;background-position:center;}QPushButton:pressed{background-color:rgba(255,255,255,0.4);}""")  # 切换窗口按钮样式
        self.pushbutton_size.setFixedSize(32, 32)
        self.pushbutton_size.clicked.connect(self.size_)
        self.pushbutton_size.setToolTip('切换窗口大小')

        self.lineedit_input = QLineEdit()
        self.lineedit_input.setFixedSize(int(self.width_ - 194), 80)
        self.lineedit_input.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
        self.lineedit_input.setStyleSheet("""
                                                                    QLineEdit{
                                                                        color:%s;
                                                                        font-family:"Microsoft YaHei";
                                                                        font-size:%spx;
                                                                        border-radius:0px;
                                                                        border-bottom:1px solid #E5E5E5;
                                                                        }
                                                                    QLineEdit:hover{
                                                                        border-bottom:1px solid #C1C1C1;
                                                                        }
                                                                    QLineEdit:focus{
                                                                        border-bottom:1px solid #12B7F5                                                                                
                                                                        }""" % (
            self.config['font']['color'], self.config['font']['size']))
        rx = QRegExp("[\S]*")
        validator = QRegExpValidator(self)
        validator.setRegExp(rx)
        self.lineedit_input.setValidator(validator)  # 设置屏蔽空格

        self.pushbutton_get = ButtonGet()
        self.pushbutton_get.setFixedSize(int(self.width_ - 194), 38)
        self.pushbutton_get.setText("获取")
        button_font = QtGui.QFont()
        button_font.setFamily("微软雅黑")
        button_font.setPointSize(11)
        self.pushbutton_get.setFont(button_font)

        self.hbox_lineedit = QHBoxLayout()
        self.hbox_lineedit.addStretch()
        self.hbox_lineedit.addWidget(self.lineedit_input)
        self.hbox_lineedit.addStretch()

        self.hbox_button = QHBoxLayout()
        self.hbox_button.addStretch()
        self.hbox_button.addWidget(self.pushbutton_get)
        self.hbox_button.addStretch()

        self.vbox_button = QVBoxLayout(self.label_bottom_background)
        self.vbox_button.addStretch()
        self.vbox_button.addLayout(self.hbox_lineedit)
        self.vbox_button.addLayout(self.hbox_button)
        self.vbox_button.addStretch()
        self.vbox_button.setSpacing(10)
        self.vbox_button.setContentsMargins(0, 0, 0, 0)

        self.layout_icon.addStretch()
        self.layout_icon.addWidget(self.pushbutton_setting, 0, Qt.AlignRight)
        self.layout_icon.addWidget(self.pushbutton_size, 0, Qt.AlignRight)
        self.layout_icon.addWidget(self.pushbutton_min, 0, Qt.AlignRight)
        self.layout_icon.addWidget(self.pushbutton_colse, 0, Qt.AlignRight)

        self.layout_icon.setSpacing(0)  # 外间距
        self.layout_icon.setContentsMargins(0, 0, 0, 0)  # 内间距

        self.vbox_background = QVBoxLayout(self.label_background)
        self.vbox_background.addWidget(self.label_top_background)
        self.vbox_background.addWidget(self.label_bottom_background)
        self.vbox_background.setSpacing(0)
        self.vbox_background.setContentsMargins(0, 0, 0, 0)

        self.pushbutton_logo = QPushButton(self.label_background)
        self.pushbutton_logo.setToolTip("")
        self.pushbutton_logo.setGeometry(int(self.width_ / 2 - 47 - 5), int(self.height_ / 2.7 - 47), 94, 94)
        self.pushbutton_logo.setStyleSheet("""QPushButton{
                                                                                border-image: url('./image/logo.png');
                                                                                }""")

        self.menu_tool = QtWidgets.QMenu(self.pushbutton_setting)

        self.menu_dir = QtWidgets.QMenu("打开目录", self.menu_tool)
        self.open_dir = QtWidgets.QAction("软件目录", self.menu_dir)
        self.open_path = QtWidgets.QAction("下载目录", self.menu_dir)
        self.menu_dir.addAction(self.open_dir)
        self.menu_dir.addAction(self.open_path)

        self.menu_real = QtWidgets.QMenu("直播平台", self.menu_tool)
        self.menu_real.mouseReleaseEvent = self.mouse_release_event_real_
        self.real_douyu = QtWidgets.QAction("斗鱼直播", self.menu_real)
        self.real_huya = QtWidgets.QAction("虎牙直播", self.menu_real)
        self.real_bili = QtWidgets.QAction("哔哩直播", self.menu_real)
        self.real_douyin = QtWidgets.QAction("抖音直播", self.menu_real)
        self.real_yy = QtWidgets.QAction("歪歪直播", self.menu_real)
        self.real_kuwo = QtWidgets.QAction("酷我直播", self.menu_real)
        self.real_kugou = QtWidgets.QAction("酷狗直播", self.menu_real)
        self.menu_real.addAction(self.real_douyu)
        self.menu_real.addAction(self.real_huya)
        self.menu_real.addAction(self.real_bili)
        self.menu_real.addAction(self.real_douyin)
        self.menu_real.addAction(self.real_yy)
        self.menu_real.addAction(self.real_kuwo)
        self.menu_real.addAction(self.real_kugou)
        self.real_douyu.setCheckable(True)
        self.real_huya.setCheckable(True)
        self.real_bili.setCheckable(True)
        self.real_douyin.setCheckable(True)
        self.real_yy.setCheckable(True)
        self.real_kuwo.setCheckable(True)
        self.real_kugou.setCheckable(True)

        self.menu_about = QtWidgets.QMenu("关于软件", self.menu_tool)
        self.about_down = QtWidgets.QAction("下载地址", self.menu_about)
        self.about_project = QtWidgets.QAction("开源项目", self.menu_about)
        self.about_explain = QtWidgets.QAction("软件说明", self.menu_about)
        self.menu_about.addAction(self.about_down)
        self.menu_about.addAction(self.about_project)
        self.menu_about.addAction(self.about_explain)
        self.about_down.triggered.connect(self.url_down_)
        self.about_project.triggered.connect(self.url_project_)
        self.about_explain.triggered.connect(self.explain_)

        self.menu_setting = QtWidgets.QMenu("其它设置", self.menu_tool)
        self.setting_rid = QtWidgets.QAction("批量获取", self.menu_setting)
        self.setting_background = QtWidgets.QAction("背景设置", self.menu_setting)
        self.setting_font_size = QtWidgets.QAction("字体大小", self.menu_setting)
        self.setting_font_color = QtWidgets.QAction("字体颜色", self.menu_setting)
        self.setting_reset = QtWidgets.QAction("重置设置", self.menu_setting)
        self.menu_setting.addAction(self.setting_rid)
        self.menu_setting.addAction(self.setting_background)
        self.menu_setting.addAction(self.setting_font_size)
        self.menu_setting.addAction(self.setting_font_color)
        self.menu_setting.addAction(self.setting_reset)

        self.menu_tool.addMenu(self.menu_dir)
        self.menu_tool.addMenu(self.menu_real)
        self.menu_tool.addMenu(self.menu_setting)
        self.menu_tool.addMenu(self.menu_about)

        self.pushbutton_setting.setMenu(self.menu_tool)
        self.pushbutton_setting.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        self.initial_live()
        self.open_dir.triggered.connect(self.open_dir_)
        self.open_path.triggered.connect(self.open_path_)
        self.setting_reset.triggered.connect(self.reset_)
        self.setting_font_color.triggered.connect(self.font_color_)
        self.setting_rid.triggered.connect(self.real_rid_)
        self.setting_font_size.triggered.connect(self.font_size_)
        self.setting_background.triggered.connect(self.background_image_)
        self.pushbutton_get.clicked.connect(self.thread_get)
        self.real_douyu.triggered.connect(self.real_live_)
        self.real_huya.triggered.connect(self.real_live_)
        self.real_bili.triggered.connect(self.real_live_)
        self.real_douyin.triggered.connect(self.real_live_)
        self.real_yy.triggered.connect(self.real_live_)
        self.real_kuwo.triggered.connect(self.real_live_)
        self.real_kugou.triggered.connect(self.real_live_)
        self.pushbutton_logo.clicked.connect(lambda: self.real_window())

    def real_rid_(self):
        self.real_rid_list = RidList()
        self.real_rid_list.setWindowModality(Qt.ApplicationModal)  # 禁止非当前窗口操作
        self.real_rid_list.show()

    def url_project_(self):
        url = 'https://github.com/s282730788/RealTool'
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def explain_(self):

        QMessageBox.information(self,
                                "关于RealTool",
                                "本软件由吾爱岚瑟首发，现已开源\n仅作为个人学习使用，不得用于任何商业用途！",
                                QMessageBox.Ok)

    def url_down_(self):
        url = 'https://lanzou.com/b00w74arg'
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        self.lineedit_input.setText("密码1234")

    def real_window(self):
        if self.real_dict:
            self.real_list = RealList(self.real_dict)
            self.real_list.show()

    def douyin_get_room_id(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        }
        url = re.search(r'(https.*)', url).group(1)
        response = requests.head(url, headers=headers, timeout=2)
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
                                params=params, timeout=2).json()
        if response:
            return response['data']['room']['owner']['web_rid']

    def kugou_get_room_id(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        }
        res = requests.get(url, headers, timeout=2).text
        rid = re.findall('roomId=(\d+)', res)[0]
        return rid

    def thread_get(self):
        self.config = ConfigObj("config.ini", encoding="UTF8")
        rid = self.lineedit_input.text()
        rid_list = []  # 存放RID列表
        rid_list_del = []  # 去重
        if rid:
            if 'live.douyin.com' in rid:
                rid = re.findall('(\d+)', rid)[0]
            elif 'v.douyin.com' in rid:
                try:
                    rid = self.douyin_get_room_id(rid)
                except:
                    rid = ""
            elif 'live.bilibili.com' in rid:
                rid = re.search('\d+', rid).group()
            elif 'douyu.com' in rid:
                if 'rid=' in rid:
                    rid = re.findall('rid=(\d+)', rid)[0]
                else:
                    rid = re.search('\d+', rid).group()
            elif 'huya.com' in rid:
                rid = rid.split("/")[-1]
            elif 'yy.com' in rid:
                rid = re.findall('/(\d+)', rid)[0]
            elif 'kuwo.cn' in rid:
                rid = re.findall('/(\d+)', rid)[0]
            elif 'kugou.com' in rid:
                if 'channel' in rid:
                    try:
                        rid = self.kugou_get_room_id(rid)
                    except:
                        rid = ""
                else:
                    rid = re.findall('/(\d+)', rid)[0]

            rid_list.append(rid)
            self.lineedit_input.setText(rid)
            self.thread = ThreadGet(rid_list)
            self.thread._signal.connect(self.text)
            self.thread.start()
            self.pushbutton_logo.setStyleSheet("""QPushButton{
                                                                                            border-image: url('./image/logo_get.png');
                                                                                            }""")
        else:
            rid_dict = self.config['rid']
            if rid_dict:
                rid_dict = ast.literal_eval(self.config['rid'])
                for i in rid_dict:
                    rid_list.append(rid_dict[i])
                for j in rid_list:
                    if j not in rid_list_del:
                        rid_list_del.append(j)
                rid_list = rid_list_del
                self.thread = ThreadGet(rid_list)
                self.thread._signal.connect(self.text)
                self.thread.start()
                self.pushbutton_logo.setStyleSheet("""QPushButton{
                                                                                                            border-image: url('./image/logo_get.png');
                                                                                                            }""")

    def text(self, real_dict, text):
        if text == 'true':
            self.real_dict = real_dict
            self.real_window()
        elif text == 'false':
            self.lineedit_input.setText("直播源获取失败")
        self.pushbutton_logo.setStyleSheet("""QPushButton{
                                                                                        border-image: url('./image/logo.png');
                                                                                        }""")
        QApplication.processEvents()

    def real_live_(self):
        self.config = ConfigObj("config.ini", encoding="UTF8")
        self.config['real']['douyu'] = "0"
        self.config['real']['huya'] = "0"
        self.config['real']['bili'] = "0"
        self.config['real']['douyin'] = "0"
        self.config['real']['yy'] = "0"
        self.config['real']['kuwo'] = "0"
        self.config['real']['kugou'] = "0"
        if self.real_douyu.isChecked():
            self.config['real']['douyu'] = "1"
        if self.real_huya.isChecked():
            self.config['real']['huya'] = "1"
        if self.real_bili.isChecked():
            self.config['real']['bili'] = "1"
        if self.real_douyin.isChecked():
            self.config['real']['douyin'] = "1"
        if self.real_yy.isChecked():
            self.config['real']['yy'] = "1"
        if self.real_kuwo.isChecked():
            self.config['real']['kuwo'] = "1"
        if self.real_kugou.isChecked():
            self.config['real']['kugou'] = "1"
        self.config.write()

    def initial_live(self):
        self.config = ConfigObj("config.ini", encoding="UTF8")
        for real_ in self.config['real']:
            if real_ == 'douyu':
                if self.config['real'][real_] == "1":
                    self.real_douyu.setChecked(True)
            if real_ == 'huya':
                if self.config['real'][real_] == "1":
                    self.real_huya.setChecked(True)
            if real_ == 'bili':
                if self.config['real'][real_] == "1":
                    self.real_bili.setChecked(True)
            if real_ == 'douyin':
                if self.config['real'][real_] == "1":
                    self.real_douyin.setChecked(True)
            if real_ == 'yy':
                if self.config['real'][real_] == "1":
                    self.real_yy.setChecked(True)
            if real_ == 'kuwo':
                if self.config['real'][real_] == "1":
                    self.real_kuwo.setChecked(True)
            if real_ == 'kugou':
                if self.config['real'][real_] == "1":
                    self.real_kugou.setChecked(True)

    def background_image_(self):
        getcwd_file = '{}/image/'.format(os.getcwd())
        background_image, filetype = QFileDialog.getOpenFileName(self,
                                                                 "选取文件",
                                                                 getcwd_file,
                                                                 "img (*jpg;*png;*bmp)")  # 设置文件扩展名过滤,注意用双分号间隔
        if background_image:
            self.config['background'] = background_image
            self.config.write()
            self.label_top_background_image.setStyleSheet("""QLabel{
                                                                                                    border:none;
                                                                                                    border-bottom-left-radius:0px;
                                                                                                    border-bottom-right-radius:0px;
                                                                                                    border-image:url('%s');
                                                                                                    }""" % background_image)
            QApplication.processEvents()
            time.sleep(0.1)

    def font_size_(self):
        self.config = ConfigObj("config.ini", encoding="UTF8")
        font_size, ok = QInputDialog.getInt(self, "字体设置", "字体大小【整数】", int(self.config['font']['size']), 1, 70, 1)
        if ok:
            self.config['font']['size'] = font_size
            self.config.write()
            self.lineedit_input.setStyleSheet("""
                                                                                            QLineEdit{
                                                                                                color:%s;
                                                                                                font-family:"Microsoft YaHei";
                                                                                                font-size:%spx;
                                                                                                border-radius:0px;
                                                                                                border-bottom:1px solid #E5E5E5;
                                                                                                }
                                                                                            QLineEdit:hover{
                                                                                                border-bottom:1px solid #C1C1C1;
                                                                                                }
                                                                                            QLineEdit:focus{
                                                                                                border-bottom:1px solid #12B7F5                                                                                
                                                                                                }""" % (
                self.config['font']['color'], font_size))

    def font_color_(self):
        self.config = ConfigObj("config.ini", encoding="UTF8")
        font_color = QColorDialog.getColor(Qt.blue, self, "信息框颜色")
        if font_color.name():
            self.config['font']['color'] = font_color.name()
            self.config.write()
            self.lineedit_input.setStyleSheet("""
                                                                                QLineEdit{
                                                                                    color:%s;
                                                                                    font-family:"Microsoft YaHei";
                                                                                    font-size:%spx;
                                                                                    border-radius:0px;
                                                                                    border-bottom:1px solid #E5E5E5;
                                                                                    }
                                                                                QLineEdit:hover{
                                                                                    border-bottom:1px solid #C1C1C1;
                                                                                    }
                                                                                QLineEdit:focus{
                                                                                    border-bottom:1px solid #12B7F5                                                                                
                                                                                    }""" % (
                font_color.name(), self.config['font']['size']))

    def reset_(self):
        # 重置设置
        config_ini.config_()
        self.config = ConfigObj("config.ini", encoding='UTF8')
        self.width_ = int(self.config['size']['width'])
        self.height_ = int(self.config['size']['height'])
        self.size_window()
        self.lineedit_input.setStyleSheet("""
                                                                            QLineEdit{
                                                                                color:%s;
                                                                                font-family:"Microsoft YaHei";
                                                                                font-size:%spx;
                                                                                border-radius:0px;
                                                                                border-bottom:1px solid #E5E5E5;
                                                                                }
                                                                            QLineEdit:hover{
                                                                                border-bottom:1px solid #C1C1C1;
                                                                                }
                                                                            QLineEdit:focus{
                                                                                border-bottom:1px solid #12B7F5                                                                                
                                                                                }""" % (
            self.config['font']['color'], self.config['font']['size']))
        self.label_top_background_image.setStyleSheet("""QLabel{
                                                                                                border:none;
                                                                                                border-bottom-left-radius:0px;
                                                                                                border-bottom-right-radius:0px;
                                                                                                border-image:url('./image/73114636.png');
                                                                                                }""")

    def quality_(self, name):
        # 画质设置

        self.config = ConfigObj("config.ini", encoding='UTF8')
        if name == "全部画质":
            self.quality_all.setChecked(True)
            self.quality_high.setChecked(False)
            self.quality_low.setChecked(False)
            self.config['quality'] = 'all'

        elif name == "最高画质":
            self.quality_high.setChecked(True)
            self.quality_all.setChecked(False)
            self.quality_low.setChecked(False)
            self.config['quality'] = 'high'

        elif name == "最低画质":
            self.quality_low.setChecked(True)
            self.quality_all.setChecked(False)
            self.quality_high.setChecked(False)
            self.config['quality'] = 'low'
        self.config.write()

    def open_path_(self):
        # 打开直播源目录
        if not os.path.exists(os.getcwd() + "/real_save"):  # 判断文件夹是否创建
            os.makedirs(os.getcwd() + "/real_save")
        subprocess.Popen("cmd.exe /C" + "start %s" % (os.getcwd() + "/real_save"), shell=True)  # 此方法不显示黑窗口

    def open_dir_(self):
        # 打开软件目录
        subprocess.Popen("cmd.exe /C" + "start %s" % (os.getcwd()), shell=True)

    def mouse_release_event_real_(self, event):
        action = self.menu_real.actionAt(event.pos())
        if not action:
            # 没有找到action就交给QMenu自己处理
            return QtWidgets.QMenu.mouseReleaseEvent(self.menu_real, event)
        if action.property('canHide'):  # 如果有该属性则给菜单自己处理
            return QtWidgets.QMenu.mouseReleaseEvent(self.menu_real, event)
        # 找到了QAction则只触发Action
        action.activate(action.Trigger)

    def mouse_release_event_quality_(self, event):
        action = self.menu_quality.actionAt(event.pos())
        if not action:
            return QtWidgets.QMenu.mouseReleaseEvent(self.menu_quality, event)
        if action.property('canHide'):
            return QtWidgets.QMenu.mouseReleaseEvent(self.menu_quality, event)
        action.activate(action.Trigger)

    def add_shadow(self):
        # 添加阴影
        effect_shadow = QGraphicsDropShadowEffect(self)
        effect_shadow.setOffset(1, 1)  # 偏移
        effect_shadow.setBlurRadius(10)  # 阴影半径
        effect_shadow.setColor(QtCore.Qt.gray)  # 阴影颜色
        self.setGraphicsEffect(effect_shadow)  # 将设置套用到widget窗口中

    def config_ini(self):
        if not os.access("config.ini", os.F_OK):
            # 初始化config配置文件
            config_ini.config_()
        self.config = ConfigObj("config.ini", encoding='UTF8')
        self.width_ = int(int(self.config['size']['width']) * float(self.config['size']['mul']))
        self.height_ = int(int(self.config['size']['height']) * float(self.config['size']['mul']))
        self.setFixedSize(self.width_, self.height_)

    def size_(self):
        if not os.access("config.ini", os.F_OK):
            self.config_ini()
        config = ConfigObj("{}/config.ini".format(os.getcwd()), encoding='UTF8')
        if float(config['size']['mul']) >= 3:
            config['size']['mul'] = 1
        else:
            config['size']['mul'] = float(config['size']['mul']) + 0.5
        config['size']['width'] = 438
        config['size']['height'] = 338
        config.write()

        self.config = ConfigObj("config.ini", encoding='UTF8')
        self.width_ = int(int(self.config['size']['width']) * float(self.config['size']['mul']))
        self.height_ = int(int(self.config['size']['height']) * float(self.config['size']['mul']))
        self.size_window()

    def size_window(self):
        self.setFixedSize(self.width_, self.height_)
        self.label_background.setGeometry(QtCore.QRect(5, 0, self.width_ - 10, self.height_ - 10))
        self.label_top_background.setFixedSize(self.width_ - 10, int(self.height_ / 2.7))
        self.label_top_background_image.setFixedSize(self.width_ - 10, int(self.height_ / 2.7))
        self.label_bottom_background.setFixedSize(self.label_top_background.width(),
                                                  self.height_ - self.label_top_background.height() - 10)
        self.label_icon.setFixedSize(self.label_top_background.width(), 32)
        self.pushbutton_logo.setGeometry(int(self.width_ / 2 - 47 - 5), int(self.height_ / 2.7 - 47), 94, 94)
        self.pushbutton_get.setFixedSize(int(self.width_ - 194), 38)
        self.lineedit_input.setFixedSize(int(self.width_ - 194), 80)
        self.move((QtGui.QCursor.pos().x() - self.pushbutton_size.x() - 20), QtGui.QCursor.pos().y() - 16)

    def min_(self):  # 最小化窗口
        self.showMinimized()

    def close_(self):  # 关闭窗口动画
        subprocess.Popen("cmd.exe /C" + "taskkill -f -im N_m3u8DL-RE.exe", shell=True)
        self.mSysTrayIcon = None  # 软件关闭后托盘不会有残留
        self.close_animation = QPropertyAnimation(self, b"windowOpacity")
        self.close_animation.setDuration(400)  # 动画时长
        self.close_animation.setStartValue(1)  # 指定动作的初始状态
        self.close_animation.setEndValue(0)  # 指定动作的最终状态
        self.close_animation.finished.connect(self.close)
        self.close_animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            try:
                self.move(event.globalPos() - self.dragPosition)
                event.accept()
            except:
                pass

    def keyPressEvent(self, event):  # 键盘事件
        if str(event.key()) == '16777216':
            self.close_()
        if str(event.key()) == '16777220' or str(event.key()) == '16777221':
            self.thread_get()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    translator = QTranslator()
    translator.load('./qtbase_zh_CN.qm')
    app.installTranslator(translator)
    ui = MainUi()
    ui.show()
    sys.exit(app.exec_())
