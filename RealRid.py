#  -*- coding: utf-8 -*-
# @Time:2022/10/21   9:35
# @Author: Lanser
# @File:RealRid.py
# Software:PyCharm

import sys
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QLineEdit, QScrollArea, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5 import QtWidgets, QtCore, QtGui
from configobj import ConfigObj
import os
import ast
import re
import requests


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


class RidList(RoundShadow, QWidget):
    _signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(RidList, self).__init__(parent)
        self.rid_dict = {}
        self.config_ini_path = '{}/config.ini'.format(os.getcwd())
        self.setup_ui()

    def setup_ui(self):
        self.resize(550, 608)
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint)  # 隐藏标题栏且可以任务栏最小化
        # self.setMinimumSize(QtCore.QSize(550, 600))  # 设置透明窗口最小尺寸
        self.setWindowTitle("直播间列表")
        self.setWindowIcon(QtGui.QIcon("./image/icon.png"))

        self.label_bottom = QtWidgets.QLabel(self)  # 创建背景标签
        self.label_bottom.setGeometry(5, 60, 540, 540)
        self.label_bottom.setStyleSheet("""QLabel{
                                                        border:none;
                                                        border-bottom:1px solid #E9E9E9;
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
        self.label_title.setText("直播间列表")
        self.label_title.setFixedSize(100, 35)
        self.label_title.setAlignment(Qt.AlignCenter)
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
        self.label_top.setGeometry(QtCore.QRect(5, 0, 540, 60))
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
        self.move_top_left.setFixedWidth(210)
        self.move_top_left.setObjectName("move_top_title")
        self.move_top_right = MoveTop(self)
        self.move_top_right.setObjectName("move_top_title")

        self.hbox_top = QHBoxLayout(self.label_top)
        self.hbox_top.addWidget(self.move_top_left)
        self.hbox_top.addWidget(self.label_title, Qt.AlignHCenter | Qt.AlignVCenter)
        self.hbox_top.addWidget(self.move_top_right)
        self.hbox_top.addWidget(self.button_close, Qt.AlignRight)
        self.hbox_top.setContentsMargins(10, 0, 10, 0)  # 内边距
        self.hbox_top.setSpacing(0)

        self.label_scroll = QLabel(self.label_bottom)
        self.label_scroll.setMinimumSize(540, 500)
        self.label_scroll.setStyleSheet("""QLabel{

                                                        border-bottom-left-radius:5px;
                                                        border-bottom-right-radius:5px;
                                                                    }""")

        self.scroll = QScrollArea()
        self.scroll.setWidget(self.label_scroll)
        self.scroll.setGeometry(QRect(0, 0, 540, 500))  # 滚动条阈值
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("""
                                                    QScrollArea{
                                                        border-bottom-left-radius:5px;
                                                        border-bottom-right-radius:5px;
                                                        background-color:#ffffff;
                                                        border-image:url("./image/73114636_bg.png");
                                                        padding:0px 0px 5px 0px;       
                                                        }
                                             """)

        self.vbox_rid = QVBoxLayout(self.label_scroll)
        self.vbox_rid.setSpacing(0)
        self.vbox_rid.setContentsMargins(0, 0, 0, 0)  # 内边距
        self.initial_rid()

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

    def initial_rid(self):
        if os.access(self.config_ini_path, os.F_OK):
            self.config = ConfigObj(self.config_ini_path, encoding='UTF8')
            self.rid_dict = self.config['rid']
            real_height = 20
            if self.rid_dict:
                self.rid_dict = ast.literal_eval(self.config['rid'])
            else:
                self.rid_dict = {}
            for i in range(1000):
                if i in self.rid_dict.keys():
                    self.vbox_rid.addWidget(
                        self.lineedit_add(i, str(self.rid_dict[i])))
                else:
                    self.vbox_rid.addWidget(self.lineedit_add(i))
                real_height += 50
                self.label_scroll.setMinimumHeight(real_height)

    def kugou_get_room_id(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1',
        }
        res = requests.get(url, headers, timeout=2).text
        rid = re.findall('roomId=(\d+)', res)[0]
        return rid

    def get_room_id(self, url):
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

    def save_rid(self, index, rid):
        if rid:
            if 'live.douyin.com' in rid:
                rid = re.findall('(\d+)', rid)[0]
            elif 'v.douyin.com' in rid:
                try:
                    rid = self.get_room_id(rid)
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
                rid = re.findall('/(\d+)/', rid)[0]
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
            self.rid_dict.update({index: rid})


        else:
            self.rid_dict.pop(index)
        self.config['rid'] = str(self.rid_dict)
        self.config.write()
        return rid

    def lineedit_add(self, index, rid_value=None):
        lineedit_text = QLineEdit()
        lineedit_text.setFixedHeight(50)
        lineedit_text.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        lineedit_text.setStyleSheet("""QLineEdit{             
                                                                                font-family:"Microsoft YaHei";   
                                                                                border-radius:0px;
                                                                                border-bottom:1px solid #E5E5E5;
                                                                                font-size:25px;                                                            
                                                                                color:#4C4B50;          
                                                                                background-color:rgba(0,0,0,0);
                                                                                }
                                                                            QLineEdit:hover{
                                                                                border-bottom:1px solid #C1C1C1;
                                                                                }
                                                                            QLineEdit:focus{
                                                                                border-bottom:2px solid #12B7F5                                                                                
                                                                                }""")

        def set_text():
            try:
                rid = self.save_rid(index, lineedit_text.text())
                lineedit_text.setText(rid)
            except:
                lineedit_text.setText("")

        # lineedit_text.textEdited[str].connect(lambda: self.save_rid(index, lineedit_text.text()))
        lineedit_text.textEdited[str].connect(set_text)
        if rid_value:
            lineedit_text.setText(rid_value)
        return lineedit_text

    def closes(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    real_rid = RidList()
    real_rid.show()
    sys.exit(app.exec_())
