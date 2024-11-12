import math
import time
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PySide6 import QtCore
from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickPaintedItem
from cv2 import cv2
from viewmodel.waveform_area_viewmodel import WaveformAreaViewModel

# 定义一个继承自QQuickPaintedItem的类，用于绘制波形
class MaggotView(QQuickPaintedItem):
    # 定义信号，用于通知选择区域和垂直线的变化
    selectionAreaChanged = QtCore.Signal()
    verticalLineChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._canvas = None  # 用于存储绘制的画布
        self._render_num_threads = 6  # 渲染使用的线程数
        self._render_executor = ThreadPoolExecutor(self._render_num_threads)  # 线程池执行器
        self._wave_index = []  # 波形索引
        self.selection = [0.0] * 4  # 选择区域
        self.max = 0.0  # 最大值
        self.min = 0.0  # 最小值
        self.time = 0.0  # 时间
        self.drag = [0.0] * 2  # 拖动起始点
        self.drag_len = 0.0  # 拖动长度
        self.real_start = 0  # 实际开始索引
        self.real_end = 0  # 实际结束索引
        self.real_index = []  # 实际索引
        self._zoom_factor = 1.0  # 缩放因子
        self._vertical_lines = 0.0  # 垂直线位置
        self.true_index = []  # 实际波形索引

    # 获取viewmodel属性
    @property
    def _viewmodel(self) -> WaveformAreaViewModel:
        return self.property("viewmodel")

    # 定义波形索引属性
    @QtCore.Property(list, notify=selectionAreaChanged)
    def wave_index(self):
        return self._wave_index

    # 设置波形索引属性
    @wave_index.setter
    def wave_index(self, value: list):
        self._wave_index = value[0]
        self.max = value[1]
        self.min = value[2]
        self.time = value[3]
        self.real_start = value[4]
        self.real_end = value[5]
        self.real = value[6]
        self.real_index = self._wave_index[self.real_start:self.real_end]
        self.true_index = self.real[self.real_start:self.real_end]
        self.selectionAreaChanged.emit()  # 发出选择区域改变信号
        self.update()  # 更新视图

    # 选择区域的槽函数
    @QtCore.Slot(int, int, bool)
    def select(self, x, y, end_point=False):
        self.selection[2], self.selection[3] = x, y
        if not end_point:
            self.selection[0], self.selection[1] = x, y
        self.update()  # 更新视图
        return self.selection

    # 拖动波形的槽函数
    @QtCore.Slot(float, bool)
    def drag_wave(self, x, end_point=False):
        if end_point:
            self.drag[1] = x
            self.drag_len = self.drag[1] - self.drag[0]
        self.drag[0] = x
        # 计算实际开始和结束索引
        self.real_start = self.real_start - int(0.2 * self.drag_len * len(self._wave_index) // self.width())
        self.real_end = self.real_end - int(0.2 * self.drag_len * len(self._wave_index) // self.width())
        self.real_index = self._wave_index[self.real_start:self.real_end]
        self.true_index = self.real[self.real_start:self.real_end]
        self.update()  # 更新视图
        return self.drag

    # 添加垂直线的槽函数
    @QtCore.Slot(int)
    def add_vertical_line(self, x):
        self._vertical_lines = x
        self.update()  # 更新视图

    # 缩放波形的槽函数
    @QtCore.Slot(int)
    def zoom_wave(self, factor):
        if factor > 0:
            self.real_index *= 2  # 放大
        else:
            self.real_index = self._wave_index[self.real_start:self.real_end]  # 缩小
        self.update()  # 更新视图

    # 绘制函数
    def paint(self, painter):
        img = self._render()  # 渲染图像
        height = img.height() / self.window().devicePixelRatio()
        if abs(self.height() - height) > 2:
            self.setHeight(height)
        painter.drawImage(QRectF(0, 0, self.width(), height), img)  # 绘制图像
        maxn = round(self.max, 2)
        if self.width() != 0:
            time = self.selection[2] - self.selection[0]
            time = time * self.time / self.width()
            time = round(time, 2)
            painter.drawText(self.selection[2], self.selection[3], str(time) + "s")  # 绘制时间文本

        # 绘制最大值文本和线条
        painter.drawText(self.selection[0], self.selection[1], "max" + str(max(self.real[self.real_start:self.real_end])) + "μV")
        painter.drawLine(self.selection[0], self.selection[1], self.selection[2], self.selection[1])
        painter.drawLine(self._vertical_lines, 0, self._vertical_lines, self.height())
        painter.drawText(self._vertical_lines, 200,
                         str(self.real[int(self._vertical_lines * len(self._wave_index) // 400)]) + "μV")

    # 渲染函数
    def _render(self, downsample=True, test_portion=0):
        dpi = self.window().devicePixelRatio()
        logical_width = self.width() * self._zoom_factor
        width = math.ceil(logical_width * dpi)
        height = 400
        if self._canvas is None or self._canvas.shape[:2] != (height, width):
            self._canvas = img = np.zeros([height, width, 3], dtype=np.uint8)  # 创建空白画布
        else:
            img = self._canvas
        img[:] = (204, 255, 204)  # 设置背景颜色

        # 计算波形点的位置
        x = np.linspace(0, 400 * dpi, len(self.real_index)).astype(np.int32)
        x = np.reshape(np.stack((x, self.real_index), axis=-1), (-1, 2))
        self._draw_grid_and_ticks(img, width, height)  # 绘制网格和刻度
        points = np.array(x).tolist()
        if test_portion == 3:
            return
        futures = []
        for _ in range(self._render_num_threads):
            futures.append(self._render_executor.submit(
                self._render_portion, points, img,
                round(dpi)))

        [future.result() for future in futures]

        w, h, c = img.shape
        if test_portion == 2:
            return
        return QImage(img.data, h, w, h * c, QImage.Format_RGB888)  # 返回渲染后的图像

    # 绘制网格和刻度
    def _draw_grid_and_ticks(self, img, width, height):
        zero_y = height * (1 - (0 - self.min) / (self.max - self.min))
        for x in range(0, width, 100):
            cv2.line(img, (x, 0), (x, height), (200, 200, 200), 1)  # 绘制垂直网格线
            cv2.putText(img, f'{x // 100}s', (x, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)  # 绘制时间刻度
        step = (max(self.real_index) - min(self.real_index)) / 10
        step_y = (self.max - self.min) / 10
        i = 0
        for y in np.arange(min(self.real_index), max(self.real_index), step):
            steps_y = self.min + i * step_y
            i += 1
            cv2.line(img, (0, int(y)), (width, int(y)), (200, 200, 200), 1)  # 绘制水平网格线
            cv2.putText(img, f'{round(steps_y, 2)}μV', (10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)  # 绘制电压刻度
        if self.min <= 0 <= self.max:
            cv2.line(img, (0, int(zero_y)), (width, int(zero_y)), (0, 0, 255), 2)  # 绘制零电压线
            cv2.putText(img, '0μV', (10, int(zero_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)  # 标记零电压

    # 静态方法，用于渲染波形的一部分
    @staticmethod
    def _render_portion(xpos, img, thickness):
        xpos = np.array(xpos, np.int32)
        cv2.polylines(img, [xpos], isClosed=False, color=(255, 0, 0), thickness=thickness)  # 绘制波形线条