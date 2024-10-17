import math
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickPaintedItem
from cv2 import cv2

from viewmodel.waveform_page_viewmodel import WaveformPageViewModel


class TagView(QQuickPaintedItem):
    markChanged = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._mark_sequence={}
        self.axiscolor={"R":"red","W":"black","N1":"yellow","N2":"green","N3":"blue","?":"grey"}
        self.markpos_begin={"R":0,"W":20,"N1":20,"N2":20,"N3":20,"?":0}
        self.markpos_end={"R":20,"W":20,"N1":40,"N2":60,"N3":80,"?":0}

    @property
    def _page_viewmodel(self) -> WaveformPageViewModel:
        # noinspection PyTypeChecker
        return self.property("page_viewmodel")

    def paint(self, painter):
        width = self.width()
        height = self.height() 
        # 坐标轴
        painter.setPen("black")  # 坐标轴颜色
        painter.drawLine(20,0,20,100)  # 划线  从（20，0）到 （20，100）的直线 竖线
        for i in range(0,100,20):  # 画纵坐标轴 上的  每个期的短线
            painter.drawLine(18,i,20,i)
        painter.drawLine(20,100,width-20,100)  # 画横坐标轴的横线
        position=10   # 纵坐标 的  R w 等注释的位置
        for key in self.axiscolor:
            painter.setPen(self.axiscolor[key])  # 遍历设置颜色
            painter.drawText(2,position,key)  # 横坐标 纵坐标 输出文字 第三个参数key 是输出的文字
            position+=20
        scale=int((width-20)/(self._page_viewmodel.seconds/30))
        if scale<=0:
            scale=1
        for key in self._page_viewmodel._mark_sequence:
            mark=self._page_viewmodel._mark_sequence[key]
            painter.setPen(self.axiscolor[mark])
            painter.drawRect(20+int(key)*scale,self.markpos_begin[mark],scale,self.markpos_end[mark]-self.markpos_begin[mark])  # 画矩形
            painter.fillRect(20+int(key)*scale,self.markpos_begin[mark],scale,self.markpos_end[mark]-self.markpos_begin[mark],self.axiscolor[mark])






