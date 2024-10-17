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
    # type hints for Qt is rubbish
    qmlRegisterType(MaggotView, 'MaggotView', 1, 0, 'MaggotView')
    # noinspection PyTypeChecker
    qmlRegisterType(TagView, 'TagView', 1, 0, 'TagView')
    # noinspection PyTypeChecker
    qmlRegisterType(WaveformView, 'WaveformView', 1, 0, 'WaveformView')
    # noinspection PyTypeChecker
    qmlRegisterSingletonType(FrameSizes, 'FrameSizes', 1, 0, 'FrameSizes')
    # noinspection PyTypeChecker
    qmlRegisterType(TimeDeltaViewModel, 'TimeDeltaViewModel', 1, 0, 'TimeDeltaViewModel')
    # noinspection PyTypeChecker
    qmlRegisterType(WaveformPageViewModel, 'WaveformPageViewModel', 1, 0, 'WaveformPageViewModel')
    # noinspection PyTypeChecker
    qmlRegisterType(WaveformAreaViewModel, 'WaveformAreaViewModel', 1, 0, 'WaveformAreaViewModel')
    # noinspection PyTypeChecker
    qmlRegisterSingletonType(MontageRegistry, 'MontageRegistry', 1, 0, 'MontageRegistry')
    # noinspection PyTypeChecker
    qmlRegisterSingletonType(OSColors, 'OSColors', 1, 0, 'OSColors')
    # noinspection PyTypeChecker
    qmlRegisterSingletonType(AlgorithmViewModel, 'AlgorithmViewModel', 1, 0, 'AlgorithmViewModel')



    app = QApplication()
    eng = QQmlApplicationEngine()
    eng.load(QUrl.fromLocalFile(str(Path(__file__).parent / "view" / "main_page.qml")))


    loop = qasync.QEventLoop(app)
    sys.exit(loop.run_forever())


if __name__ == "__main__":
    main()