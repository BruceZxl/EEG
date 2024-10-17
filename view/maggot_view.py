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


class MaggotView(QQuickPaintedItem):
    selectionAreaChanged = QtCore.Signal()
    verticalLineChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__()
        self._canvas = None
        self._render_num_threads = 6
        self._render_executor = ThreadPoolExecutor(self._render_num_threads)
        self._wave_index = []
        self.selection = [0.0] * 4
        self.max = 0.0
        self.min = 0.0
        self.time = 0.0
        self.drag = [0.0] * 2
        self.drag_len = 0.0
        self.real_start = 0
        self.real_end = 0
        self.real_index = []
        self._zoom_factor = 1.0
        self._vertical_lines = 0.0
        self.true_index = []

    @property
    def _viewmodel(self) -> WaveformAreaViewModel:
        return self.property("viewmodel")

    @QtCore.Property(list, notify=selectionAreaChanged)
    def wave_index(self):
        return self._wave_index

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
        self.selectionAreaChanged.emit()
        self.update()

    @QtCore.Slot(int, int, bool)
    def select(self, x, y, end_point=False):
        self.selection[2], self.selection[3] = x, y
        if not end_point:
            self.selection[0], self.selection[1] = x, y
        self.update()
        return self.selection

    @QtCore.Slot(float, bool)
    def drag_wave(self, x, end_point=False):
        if end_point:
            self.drag[1] = x
            self.drag_len = self.drag[1] - self.drag[0]
        self.drag[0] = x
        self.real_start = self.real_start - int(0.2 * self.drag_len * len(self._wave_index) // self.width())
        self.real_end = self.real_end - int(0.2 * self.drag_len * len(self._wave_index) // self.width())
        self.real_index = self._wave_index[self.real_start:self.real_end]
        self.true_index = self.real[self.real_start:self.real_end]
        self.update()
        return self.drag

    @QtCore.Slot(int)
    def add_vertical_line(self, x):
        self._vertical_lines = x
        self.update()

    @QtCore.Slot(int)
    def zoom_wave(self, factor):
        if factor> 0:
            self.real_index *= 2
        else:
            self.real_index =self._wave_index[self.real_start:self.real_end]
        self.update()

    def paint(self, painter):
        img = self._render()
        height = img.height() / self.window().devicePixelRatio()
        if abs(self.height() - height) > 2:
            self.setHeight(height)
        painter.drawImage(QRectF(0, 0, self.width(), height), img)
        maxn = round(self.max, 2)
        if self.width() != 0:
            time = self.selection[2] - self.selection[0]
            time = time * self.time / self.width()
            time = round(time, 2)
            painter.drawText(self.selection[2], self.selection[3], str(time) + "s")

        painter.drawText(self.selection[0], self.selection[1], "max" + str(max(self.real[self.real_start:self.real_end])) + "μV")
        painter.drawLine(self.selection[0], self.selection[1], self.selection[2], self.selection[1])
        painter.drawLine(self._vertical_lines, 0, self._vertical_lines, self.height())
        painter.drawText(self._vertical_lines, 200,
                     str(self.real[int(self._vertical_lines*len(self._wave_index)//400)]) + "μV")
    def _render(self, downsample=True, test_portion=0):
        dpi = self.window().devicePixelRatio()
        logical_width = self.width() * self._zoom_factor
        width = math.ceil(logical_width * dpi)
        height = 400
        if self._canvas is None or self._canvas.shape[:2] != (height, width):
            self._canvas = img = np.zeros([height, width, 3], dtype=np.uint8)
        else:
            img = self._canvas
        img[:] = (204, 255, 204)



        x = np.linspace(0, 400 * dpi, len(self.real_index)).astype(np.int32)
        x = np.reshape(np.stack((x, self.real_index), axis=-1), (-1, 2))
        self._draw_grid_and_ticks(img, width, height)
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
        return QImage(img.data, h, w, h * c, QImage.Format_RGB888)

    def _draw_grid_and_ticks(self, img, width, height):
        zero_y = height * (1 - (0 - self.min) / (self.max - self.min))
        for x in range(0, width, 100):
            cv2.line(img, (x, 0), (x, height), (200, 200, 200), 1)
            cv2.putText(img, f'{x // 100}s', (x, height - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        step = ( max(self.real_index) -min(self.real_index)) / 10
        step_y = (self.max-self.min)/10
        i = 0
        for y in np.arange(min(self.real_index), max(self.real_index), step):
            steps_y = self.min + i*step_y
            i += 1
            cv2.line(img, (0, int(y)), (width, int(y)), (200, 200, 200), 1)
            cv2.putText(img, f'{round(steps_y, 2)}μV', (10, int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        if self.min <= 0 <= self.max:
            cv2.line(img, (0, int(zero_y)), (width, int(zero_y)), (0, 0, 255), 2)
            cv2.putText(img, '0μV', (10, int(zero_y)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    @staticmethod
    def _render_portion(xpos, img, thickness):
        xpos = np.array(xpos, np.int32)
        cv2.polylines(img, [xpos], isClosed=False, color=(255, 0, 0), thickness=thickness)
