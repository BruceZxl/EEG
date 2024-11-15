import re
import sys
from pathlib import Path

import qasync
from PySide6 import QtCore
from PySide6.QtCore import QUrl
from PySide6.QtQml import qmlRegisterType, QQmlApplicationEngine, qmlRegisterSingletonType
from PySide6.QtWidgets import QApplication
from loguru import logger

from view.os_colors import OSColors
from view.waveform_view import WaveformView
from viewmodel.frame_sizes import FrameSizes
from viewmodel.montage_registry import MontageRegistry
from viewmodel.time_delta_viewmodel import TimeDeltaViewModel
from viewmodel.waveform_area_viewmodel import WaveformAreaViewModel
from viewmodel.waveform_page_viewmodel import WaveformPageViewModel
from algorithm.MDD.Depression_algorithm_zxy_ls import AlgorithmViewModel
from view.tag_view import TagView
from view.maggot_view import MaggotView

def qt_message_handler(mode, context, message):
    mode = mode.name.decode("ascii")[2:-3]
    try:
        level, mode = logger.level(mode.upper()), ''
    except ValueError:
        level, mode = logger.info, f"[{mode}] "
    if ".qml:" in message:
        message = re.sub(r"\.qml:(\d)", r".qml: \1", message)
    else:
        message=f"{context.file}: {context.line:d}: {message}"
    logger.opt().log(level[0], f"{mode}{message}")


def main():
    QtCore.qInstallMessageHandler(qt_message_handler)

    app = QApplication()
    eng = QQmlApplicationEngine()

    # 创建 ViewModel 实例
    viewmodel = WaveformPageViewModel()

    # 将实例设置到 QML 上下文中
    eng.rootContext().setContextProperty("viewmodel", viewmodel)

    # 注册其他类型
    qmlRegisterType(MaggotView, 'MaggotView', 1, 0, 'MaggotView')
    qmlRegisterType(TagView, 'TagView', 1, 0, 'TagView')
    qmlRegisterType(WaveformView, 'WaveformView', 1, 0, 'WaveformView')
    qmlRegisterSingletonType(FrameSizes, 'FrameSizes', 1, 0, 'FrameSizes')
    qmlRegisterType(TimeDeltaViewModel, 'TimeDeltaViewModel', 1, 0, 'TimeDeltaViewModel')
    # 保留这行注册
    qmlRegisterType(WaveformPageViewModel, 'WaveformPageViewModel', 1, 0, 'WaveformPageViewModel')
    qmlRegisterType(WaveformAreaViewModel, 'WaveformAreaViewModel', 1, 0, 'WaveformAreaViewModel')
    qmlRegisterSingletonType(MontageRegistry, 'MontageRegistry', 1, 0, 'MontageRegistry')
    qmlRegisterSingletonType(OSColors, 'OSColors', 1, 0, 'OSColors')
    qmlRegisterSingletonType(AlgorithmViewModel, 'AlgorithmViewModel', 1, 0, 'AlgorithmViewModel')


    #注册方法
    logic1 = WaveformPageViewModel()
    eng.rootContext().setContextProperty("WaveformPageViewModel", logic1)
    logic2 = WaveformView()
    eng.rootContext().setContextProperty("WaveformView", logic2)
    # 加载 QML 文件
    eng.load(QUrl.fromLocalFile(str(Path(__file__).parent / "view" / "main_page.qml")))

    loop = qasync.QEventLoop(app)
    sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()