#  -*- coding: utf-8 -*-
# @Time:2022/10/15   5:41
# @Author: 须尽欢
# @File:RealListWindow.py
# Software:PyCharm

import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QScrollArea, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.Qt import QRegExp, QRegExpValidator
from PyQt5 import QtWidgets, QtCore, QtGui
import pyperclip
import os
import subprocess
import win32api
import requests
import time
from configobj import ConfigObj


class ThreadRec(QtCore.QThread):
    def __init__(self, live_name, url_link, rid, url_name):
        super(ThreadRec, self).__init__()
        self.live_name = live_name
        self.url_link = url_link
        self.rid = rid
        self.url_name = url_name

    def run(self):
        path_down = '{}/real_save/{}/Downloads'.format(os.getcwd(), self.rid)
        if not os.path.exists(path_down):
            os.makedirs(path_down)

        if ".m3u8" in self.url_link:
            path_down.replace("/", "\\")
            live_url = self.url_link
            live_url = live_url.replace("&", "^&^")
            live_url = live_url.replace("^^", "^")
            rec = 'N_m3u8DL-RE_Beta_win-x64\\N_m3u8DL-RE.exe "{}" --tmp-dir "{}" --save-dir "{}" --save-name "{}_{}_{}" --live-real-time-merge --del-after-done'.format(
                live_url, path_down, path_down, self.live_name, self.rid,
                time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()))
            with open("rec.bat", "w", encoding="utf-8") as f:
                f.write(rec)
            win32api.ShellExecute(0, 'open', 'rec.bat', '', '', 1)  # 前台打开

        elif ".flv" in self.url_link or ".xs" in self.url_link:
            try:
                response = requests.get(self.url_link, stream=True)
                f = open("{}/{}_{}_{}.flv".format(path_down, self.live_name, self.url_name,
                                                  time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())), "ab")
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                    else:
                        f.close()
            except:
                pass


class ButtonTitle(QtWidgets.QPushButton):
    def __init__(self, name, border_color, parent=None):
        super().__init__(parent)
        self.name = name
        self.setFixedSize(100, 33)
        self.setToolTip("全部保存")
        self.setStyleSheet("""QPushButton{
                                                border-radius:0px;
                                                border-top-left-radius:10px;
                                                border-top-right-radius:10px;
                                                font-family:"Microsoft YaHei";
                                                color:#ffffff;
                                                font-size:18px;
                                                font-weight: bold;
                                                background-color: %s;  }
                                                        }""" % border_color)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # 鼠标指针变成手抓状
        self.setText(name)

    def enterEvent(self, event):  # 进入
        self.setText("保存")
        super().enterEvent(event)

    def leaveEvent(self, event):  # 离开
        self.setText(self.name)
        super().leaveEvent(event)


class PushButton(QPushButton):
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
        self.button_stylesheet = pushbutton_stylesheet

        self._animation = QtCore.QVariantAnimation(  # 创建一个动画
            startValue=0,
            endValue=100,
            valueChanged=self._on_value_changed,  # 更改值的函数
            duration=duration,
        )
        self._update_stylesheet(self.button_bg)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))  # 鼠标指针变成手抓状

    def _on_value_changed(self, a):  # 更新 改变后的值
        a = a / 100 * self.background_color_rgba + self.button_bg
        self._update_stylesheet(a)  # 更新并调用样式

    def _update_stylesheet(self, a):  # 更新样式函数

        self.setStyleSheet("""QPushButton{background-image: url(%s);
                              background-color:rgba(%s,%s);
                              %s}

                              """ % (
            self.background_img, self.background_color_rgb, a, self.button_stylesheet))

    def enterEvent(self, event):  # 进入
        self._animation.setDirection(QtCore.QAbstractAnimation.Forward)  # 正
        self._animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):  # 离开
        self._animation.setDirection(QtCore.QAbstractAnimation.Backward)  # 反
        self._animation.start()
        super().leaveEvent(event)


class RoundShadow(QWidget):
    """圆角边框类"""

    def __init__(self, parent=None):
        super(RoundShadow, self).__init__(parent)
        self.border_width = 10
        # 设置 窗口无边框和背景透明 *必须
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

    def paintEvent(self, event):
        # 阴影
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)

        pat = QtGui.QPainter(self)
        pat.setRenderHint(pat.Antialiasing)
        pat.fillPath(path, QtGui.QBrush(Qt.white))

        color = QtGui.QColor(192, 192, 192, 50)

        for i in range(10):
            i_path = QtGui.QPainterPath()
            i_path.setFillRule(Qt.WindingFill)
            ref = QtCore.QRectF(10 - i, 10 - i, self.width() - (10 - i) * 2, self.height() - (10 - i) * 2)
            # i_path.addRect(ref)
            i_path.addRoundedRect(ref, self.border_width, self.border_width)
            color.setAlpha(int(150 - i ** 0.5 * 50))
            pat.setPen(color)
            pat.drawPath(i_path)

        # 圆角
        pat2 = QtGui.QPainter(self)
        pat2.setRenderHint(pat2.Antialiasing)  # 抗锯齿
        pat2.setBrush(Qt.white)
        pat2.setPen(Qt.transparent)


class MoveTop(QWidget):
    def __init__(self, parent):
        super(MoveTop, self).__init__()
        self.win = parent
        self.InitializeWindow()
        self.setStyleSheet("""
        QWidget{
            background-color:rgba(255,0,255,0);
            border:none;
            margin:0px;
                }""")

    def InitializeWindow(self):
        self.isPressed = False
        top = QLabel()
        layout_h = QHBoxLayout()
        layout_h.addWidget(top)
        self.setLayout(layout_h)

    def mousePressEvent(self, event):  # 设置鼠标拖动Label
        if event.button() == Qt.LeftButton:  # 如果鼠标按钮等于左键
            self.isPressed = True
            self.startPos = event.globalPos()
            return QWidget().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:  # 如果鼠标按钮等于左键
            self.isPressed = False
            return QWidget().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if self.isPressed:
            if self.win.isMaximized:
                self.win.showNormal()

            movePos = event.globalPos() - self.startPos
            self.startPos = event.globalPos()
            self.win.move(self.win.pos() + movePos)

        return QWidget().mouseMoveEvent(event)


class RealList(RoundShadow, QWidget):
    _signal = QtCore.pyqtSignal(str)

    def __init__(self, real_dict, parent=None):
        super(RealList, self).__init__(parent)
        self.real_dict = real_dict
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)  # 隐藏标题栏且可以任务栏最小化
        self.setMinimumSize(QtCore.QSize(850, 610))  # 设置透明窗口最小尺寸
        self.setWindowTitle("直播源列表")
        self.setWindowIcon(QtGui.QIcon("./image/icon.png"))

        self.label_bottom = QtWidgets.QLabel(self)  # 创建背景标签
        self.label_bottom.setGeometry(5, 60, 840, 540)
        self.label_bottom.setStyleSheet("""QLabel{
                                                        border:none;
                                                        border-bottom:1px solid #E7E7E7;
                                                        background-color:rgba(255,255,255,1);
                                                        border-bottom-left-radius:5px;
                                                        border-bottom-right-radius:5px;
                                                        }
                                                        """)
        self.button_close = PushButton("./image/close_icon_2.png", "0,0,0", 0, 200, 0,
                                       '''border:none;background-repeat:no-repeat;background-position:center;margin-right:0px;border-radius:5px;}QPushButton:hover{background-image:url(./image/close_icon_3.png);''')
        self.button_close.setObjectName("pushButton_close")
        self.button_close.setMinimumSize(QtCore.QSize(39, 39))
        self.button_close.setMaximumSize(QtCore.QSize(39, 39))
        self.button_close.setToolTip("关闭")

        self.label_title = QLabel()
        self.label_title.setFixedSize(100, 35)
        self.label_title.setAlignment(Qt.AlignCenter)
        self.label_title.setText("直播源列表")
        self.label_title.setStyleSheet("""QLabel{                                                    
                                                    border:none;
                                                    border-radius:16px;     
                                                    font-family:"Microsoft YaHei";
                                                    font-weight:bold;
                                                    text-align:center;
                                                    color:#474747;
                                                    font-size:16px;       
                                                    background-color:none;;                                                           
                                                    }
                                                    """)

        self.label_top = QLabel(self)
        self.label_top.setGeometry(QtCore.QRect(5, 0, 840, 60))
        self.label_top.setStyleSheet("""
                                                            QLabel{
                                                                border-top:1px solid #E9E9E9;
                                                                border-bottom:1px solid #E7E7E7;
                                                                background-color:rgba(255,255,255,1);
                                                                border-top-left-radius:5px;
                                                                border-top-right-radius:5px;
                                                            }
                                                            """)

        self.move_top_left = MoveTop(self)
        self.move_top_left.setFixedWidth(310)
        self.move_top_left.setObjectName("move_top_title")
        self.move_top_right = MoveTop(self)
        self.move_top_right.setObjectName("move_top_title")

        self.hbox_top = QHBoxLayout(self.label_top)
        self.hbox_top.addWidget(self.move_top_left)
        self.hbox_top.addWidget(self.label_title, Qt.AlignHCenter | Qt.AlignVCenter)
        self.hbox_top.addWidget(self.move_top_right)
        self.hbox_top.addWidget(self.button_close, Qt.AlignRight)
        self.hbox_top.setContentsMargins(60, 0, 10, 0)  # 内边距
        self.hbox_top.setSpacing(0)

        self.label_scroll = QLabel(self.label_bottom)
        self.label_scroll.setMinimumSize(840, 500)
        self.label_scroll.setStyleSheet("""QLabel{                                                        
                                                        border-bottom-left-radius:5px;
                                                        border-bottom-right-radius:5px;
                                                                    }""")

        self.scroll = QScrollArea()  # 创建一个滚动条
        self.scroll.setWidget(self.label_scroll)
        self.scroll.setGeometry(QRect(0, 0, 840, 500))  # 滚动条阈值
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 不显示水平滚动条
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 不显示垂直滚动条
        self.scroll.setStyleSheet("""
                                                    QScrollArea{
                                                        border-bottom-left-radius:5px;
                                                        border-bottom-right-radius:5px;
                                                        background-color:#ffffff;
                                                        border-image:url("./image/73114636_bg.png");
                                                        padding:0px 0px 5px 0px;                                                    
                                                        }
                                             """)

        self.add_layout()
        self.vbox_widget = QVBoxLayout(self)
        self.vbox_widget.addLayout(self.hbox_top)
        self.vbox_widget.addWidget(self.scroll)
        self.vbox_widget.setContentsMargins(5, 60, 5, 10)  # 内边距
        self.vbox_widget.setSpacing(0)
        self.button_close.clicked.connect(self.closes)

    def label_text(self, text):
        self.label_title.setText(text)
        self.label_text_animation = QtCore.QVariantAnimation(  # 创建一个动画
            startValue=0,
            endValue=100,
            valueChanged=self._update_stylesheet,  # 更改值的函数
            duration=1500,
        )
        self.label_text_animation.start()

    def _update_stylesheet(self, a):  # 更新样式函数
        b = 1 - (100 - (a * 2)) / 100
        if b >= 1:
            b = (100 - a) / 50
            if b <= 0:
                self.label_title.setText("直播源列表")
                b = 1
        self.label_title.setStyleSheet("""QLabel{                                                    
                                                    border:none;
                                                    border-radius:16px;     
                                                    font-family:"Microsoft YaHei";
                                                    font-weight:bold;
                                                    text-align:center;
                                                    color:rgba(71,71,71, %s);
                                                    font-size:16px;       
                                                    background-color:none;;                                                           
                                                    }
                                                    """ % b)

    def add_layout_title_save_all(self, live_name, url_dict, border_color, rid,
                                  nick_name):  # 平台名称，链接字典，border颜色，rid， 用户名称

        def save(url_link, url_name, count):
            save_path = "{}/real_save/{}".format(os.getcwd(), rid)
            if not os.path.exists("{}/real_save/{}".format(os.getcwd(), rid)):
                os.makedirs(
                    "{}/real_save/{}".format(os.getcwd(), rid))
            asx_path = "{}/{}_{}_{}_{}.asx".format(save_path, live_name, url_name, count, nick_name)
            if url_link:
                asx_str = """
                <asx version = "3.0" >
                <entry>
                <title>{}_{}_{}</title>
                <ref href = "{}"/>
                </entry>
                </asx>
                """.format(live_name, url_name, nick_name, url_link)
                with open(asx_path, "w", encoding="UTF8") as f:
                    f.write(asx_str)

        def save_all():
            for count, real_one in enumerate(url_dict):
                for url_name in real_one:
                    save(real_one[url_name], url_name, count)
            self.label_text("全部保存成功")

        button_title_save_all = ButtonTitle(live_name, border_color)
        button_title_save_all.clicked.connect(save_all)

        label_rid = QLabel()
        label_rid.setText(rid)
        label_rid.setFixedHeight(33)
        label_rid.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label_rid.setStyleSheet("""QLabel{
                                                                    color:%s;
                                                                    font-size:18px;
                                                                    font-family:"Microsoft YaHei";
                                                                    font-weight: bold;
                                                                    }""" % border_color)

        label_name = QLabel()
        label_name.setText(nick_name)
        label_name.setFixedWidth(400)
        label_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label_name.setStyleSheet("""QLabel{
                                                                            color:%s;
                                                                            font-size:18px;
                                                                            font-family:"Microsoft YaHei";
                                                                            font-weight: bold;
                                                                            }""" % border_color)

        hbox_title = QHBoxLayout()
        hbox_title.addWidget(button_title_save_all)
        hbox_title.addWidget(label_rid)
        hbox_title.addStretch()
        hbox_title.addWidget(label_name)
        hbox_title.setContentsMargins(0, 0, 20, 0)  # 内边距
        hbox_title.setSpacing(20)

        return hbox_title

    def add_layout_url(self, live_name, url_name, url_link, border_color, count, rid,
                       nick_name):  # 平台名称，链接名称， 链接地址， border颜色，链接计数，用户名称
        label_name = QLabel()
        label_name.setText(url_name)
        label_name.setFixedSize(160, 32)
        label_name.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label_name.setStyleSheet("""QLabel{                   
                                                                border:none;  
                                                                border-radius:5px;          
                                                                border-bottom-right-radius:0px;                                          
                                                                font-family:"Microsoft YaHei";
                                                                color:#ffffff;
                                                                font-size:16px;
                                                                background-color: %s;                                                                        
                                                                }""" % border_color)
        lineedit_url = QLineEdit()
        lineedit_url.setFixedSize(600, 32)
        lineedit_url.setText(url_link)
        lineedit_url.setStyleSheet("""QLineEdit{
                                                            padding:0px 150px 0px 10px;                                                          
                                                            border:none;
                                                            font-family:"Microsoft YaHei";
                                                            font-size:16px;
                                                            border-bottom:1px solid %s;
                                                            color:#4C4B50;
                                                            text-align:left;
                                                            background-color:rgba(255,255,255,0);
                                                            }
                                                            QLineEdit:hover{
                                                            border-bottom:2px solid %s;}
                                                            QLineEdit:focus{
                                                            border-bottom:2px solid %s;}
                                                            """ % (border_color, border_color, border_color))
        rx = QRegExp("[\S]*")
        validator = QRegExpValidator()
        validator.setRegExp(rx)
        lineedit_url.setValidator(validator)  # 设置屏蔽空格

        def button_qss(image):
            button_qss = """QPushButton{
                                                                border: 2px solid %s;
                                                                border-radius:5px;
                                                                background-color:%s;
                                                                border-image:url(./image/%s);
                                                                }
                                                        QPushButton:hover{
                                                                border:0px solid %s;
                                                                }""" % (border_color, border_color, image, border_color)
            return button_qss

        def copy_():
            pyperclip.copy(url_link)
            self.label_text("复制成功")

        button_copy = QPushButton()
        button_copy.setFixedSize(28, 28)
        button_copy.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button_copy.setToolTip('复制')
        button_copy.setStyleSheet(button_qss('copy.png'))
        button_copy.clicked.connect(copy_)

        button_save = QPushButton()
        button_save.setFixedSize(28, 28)
        button_save.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button_save.setToolTip('保存')
        button_save.setStyleSheet(button_qss('save.png'))
        button_save.clicked.connect(lambda: asx_("save", rid))

        button_play = QPushButton()
        button_play.setFixedSize(28, 28)
        button_play.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button_play.setToolTip('播放')
        button_play.setStyleSheet(button_qss('play.png'))
        button_play.clicked.connect(lambda: player_())

        button_rec = QPushButton()
        button_rec.setFixedSize(28, 28)
        button_rec.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        button_rec.setToolTip('录制')
        button_rec.setStyleSheet(button_qss('rec.png'))
        button_rec.clicked.connect(lambda: asx_("rec", rid))

        def player_():
            config = ConfigObj("config.ini", encoding='UTF8')
            if config['player'] == 'pot':
                asx_('play', rid)
            elif config['player'] == 'mpv':
                mpv_path = '\"%s\"' % config['mpv']
                subprocess.Popen("cmd.exe /C %s %s" % (mpv_path, url_link), shell=True)

        def asx_(text, rid_):
            save_path = "{}/real_save/{}".format(os.getcwd(), rid_)
            if not os.path.exists("{}/real_save/{}".format(os.getcwd(), rid_)):
                os.makedirs(
                    "{}/real_save/{}".format(os.getcwd(), rid_))

            asx_path = "{}/{}_{}_{}_{}.asx".format(save_path, live_name, url_name, count, nick_name)

            def save():
                if url_link:
                    asx_str = """
                    <asx version = "3.0" >
                    <entry>
                    <title>{}_{}_{}</title>
                    <ref href = "{}"/>
                    </entry>
                    </asx>
                    """.format(live_name, url_name, nick_name, url_link)

                    with open(asx_path, "w", encoding="UTF8") as f:
                        f.write(asx_str)

            if text == "save":
                save()
                self.label_text("保存成功")
            elif text == "play":
                save()
                os.startfile(asx_path)
                self.label_text("打开文件")
            elif text == 'rec':
                self.thread_rec = ThreadRec(live_name, url_link.strip(), rid_, url_name)
                self.thread_rec.start()
                self.label_text("正在录制...")
                button_rec.setStyleSheet("""QPushButton{
                                                            border:0px solid #20D68D;
                                                            border-radius:5px;
                                                            background-color:#20D68D;
                                                            border-image:url(./image/rec);
                                                            }
                                                    """)

        hbox_tool = QHBoxLayout(lineedit_url)
        hbox_tool.addStretch()
        hbox_tool.addWidget(button_copy, Qt.AlignHCenter | Qt.AlignTop)

        hbox_tool.addWidget(button_save)
        hbox_tool.addWidget(button_play)
        hbox_tool.addWidget(button_rec)
        hbox_tool.setContentsMargins(0, 0, 0, 0)  # 内边距
        hbox_tool.setSpacing(3)

        hbox_url = QHBoxLayout()
        hbox_url.addWidget(label_name)
        hbox_url.addWidget(lineedit_url)
        hbox_url.addStretch()
        hbox_url.setContentsMargins(0, 0, 0, 0)  # 内边距
        hbox_url.setSpacing(0)
        return hbox_url

    def add_layout(self):
        if self.real_dict:
            vbox_real = QVBoxLayout(self.label_scroll)
            vbox_real.setSpacing(0)
            vbox_real.setContentsMargins(20, 0, 0, 0)  # 内边距
            real_height = 0
            border_color = '#FF7701'
            for name in self.real_dict:
                if "douyu" in name:
                    border_color = '#FF7701'
                elif "bili" in name:
                    border_color = '#00AEEC'
                elif 'douyin' in name:
                    border_color = '#FE2B54'
                elif 'huya' in name:
                    border_color = '#FFAB08'
                elif 'yy' in name:
                    border_color = '#FFE600'
                elif 'kuwo' in name:
                    border_color = '#CB83F7'
                elif 'kugou' in name:
                    border_color = '#01D07F'
                elif 'yizhibo' in name:
                    border_color = '#2B2C2E'

                vbox_list = QVBoxLayout()
                vbox_list.setSpacing(0)
                hbox_title = QHBoxLayout()
                real_height += 62
                list_height = 0
                label_url_background = QLabel()
                label_url_background.setStyleSheet("""QLabel{                                                
                                                                                        border:2px solid %s;
                                                                                        border-top-right-radius:5px;
                                                                                        border-bottom-left-radius:5px;
                                                                                        border-bottom-right-radius:5px;
                                                                                        }""" % border_color)

                hbox_title.addLayout(self.add_layout_title_save_all(name, self.real_dict[name], border_color,
                                                                    self.real_dict[name][-1]['rid'],
                                                                    self.real_dict[name][-2]['name']))
                vbox_url = QVBoxLayout(label_url_background)
                for count, url_dict in enumerate(self.real_dict[name]):
                    real_height += 80
                    list_height += 80
                    label_url_background.setFixedSize(800, list_height)
                    vbox_list.addLayout(hbox_title)
                    vbox_list.addWidget(label_url_background)
                    vbox_list.setContentsMargins(0, 30, 0, 0)  # 内边距
                    vbox_list.setSpacing(0)
                    for url_name in url_dict:
                        if url_name != 'rid' and url_name != 'name':
                            vbox_url.addLayout(
                                self.add_layout_url(name, url_name, url_dict[url_name], border_color, count,
                                                    self.real_dict[name][-1]['rid'], self.real_dict[name][-2]['name']))
                    self.label_scroll.setMinimumHeight(real_height)
                    vbox_real.addLayout(vbox_list)
            vbox_real.addStretch()

    def add_text_(self, text):
        self._signal.emit(text)

    def closes(self):  # 关闭窗口
        self.close()


if __name__ == '__main__':
    real_dict_ = {'douyu': [{'原画_flv': 'http://ws-tct.douyucdn.cn/live/6rdygfhd.flv?uuid='},
                            {'原画_m3u8': 'http://ws-tct.douyucdn.cn/live/6rdygfhd.m3u8?uuid='},
                            {'原画_x_p2p': 'http://ws-tct.douyucdn.cn/live/6rdygfhd.xs?uuid='},
                            {'高清_flv': 'http://ws-tct.douyucdn.cn/live/6rdygfhd_2000.flv?uuid='},
                            {'高清_m3u8': 'http://ws-tct.douyucdn.cn/live/6rdygfhd_2000.m3u8?uuid='},
                            {'高清_x_p2p': 'http://ws-tct.douyucdn.cn/live/6rdygfhd_2000.xs?uuid='}, {'name': '斗鱼官方直播'},
                            {'rid': '6'}], 'bili': [{
        '线路1_10000': 'https://d1--cn-gotcha208.bilivideo.com/live-bvc/779788/live_50329118_9516950_bluray/index.m3u8?expires=1668276677&len=0&oi=1996077206&pt=web&qn=10000&trid=1007920b1c6ee6d349bea1cfd76324335aac&sigparams=cdn,expires,len,oi,pt,qn,trid&cdn=cn-gotcha208&sign=606162f239f4bb86e617278699a75412&sk=c9c6154426932efa80d25af02e87a3bd&p2p_type=1&src=57345&sl=10&free_type=0&pp=rtmp&machinezone=ylf&source=onetier&site=41084a238fdf53253ad6d6924866b8ea&order=1'},
        {
            '线路2_10000': 'https://cn-hbyc-ct-02-28.bilivideo.com/live-bvc/779788/live_50329118_9516950_bluray/index.m3u8?expires=1668276677&len=0&oi=1996077206&pt=web&qn=10000&trid=1007920b1c6ee6d349bea1cfd76324335aac&sigparams=cdn,expires,len,oi,pt,qn,trid&cdn=cn-gotcha01&sign=c2792b36c2e5151db1bde3b257d5e1a3&sk=c9c6154426932efa80d25af02e87a3bd&flvsk=2935686d6cb9146c7a6a6a0b4e120e2557adc0b48de99725a5887e843ee476a1&p2p_type=1&src=57345&sl=10&free_type=0&sid=cn-hbyc-ct-02-28&chash=0&sche=ban&bvchls=1&score=18&pp=rtmp&machinezone=ylf&source=onetier&site=41084a238fdf53253ad6d6924866b8ea&order=2'},
        {
            '线路2_2500': 'https://cn-hbyc-ct-02-28.bilivideo.com/live-bvc/779788/live_50329118_9516950_2500/index.m3u8?expires=1668276677&len=0&oi=1996077206&pt=web&qn=2500&trid=1007920b1c6ee6d349bea1cfd76324335aac&sigparams=cdn,expires,len,oi,pt,qn,trid&cdn=cn-gotcha01&sign=c2792b36c2e5151db1bde3b257d5e1a3&sk=c9c6154426932efa80d25af02e87a3bd&flvsk=2935686d6cb9146c7a6a6a0b4e120e2557adc0b48de99725a5887e843ee476a1&p2p_type=1&src=57345&sl=10&free_type=0&sid=cn-hbyc-ct-02-28&chash=0&sche=ban&bvchls=1&score=18&pp=rtmp&machinezone=ylf&source=onetier&site=41084a238fdf53253ad6d6924866b8ea&order=2'},
        {
            '线路2_1500': 'https://cn-hbyc-ct-02-28.bilivideo.com/live-bvc/779788/live_50329118_9516950_1500/index.m3u8?expires=1668276677&len=0&oi=1996077206&pt=web&qn=1500&trid=1007920b1c6ee6d349bea1cfd76324335aac&sigparams=cdn,expires,len,oi,pt,qn,trid&cdn=cn-gotcha01&sign=c2792b36c2e5151db1bde3b257d5e1a3&sk=c9c6154426932efa80d25af02e87a3bd&flvsk=2935686d6cb9146c7a6a6a0b4e120e2557adc0b48de99725a5887e843ee476a1&p2p_type=1&src=57345&sl=10&free_type=0&sid=cn-hbyc-ct-02-28&chash=0&sche=ban&bvchls=1&score=18&pp=rtmp&machinezone=ylf&source=onetier&site=41084a238fdf53253ad6d6924866b8ea&order=2'},
        {'name': '哔哩哔哩英雄联盟赛事'}, {'rid': '6'}]}

    app = QApplication(sys.argv)
    favorites = RealList(real_dict_)
    favorites.show()
    sys.exit(app.exec_())
