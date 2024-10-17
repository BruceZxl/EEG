import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import TagView
import FrameSizes
import TimeDeltaViewModel
import WaveformPageViewModel
import WaveformAreaViewModel

//实现标注的窗口
ColumnLayout { //继承于 item类
    id:root  //元素命名
    property WaveformPageViewModel page_viewmodel
    TagView{
        property alias page_viewmodel: root.page_viewmodel //别名
        Layout.fillWidth: true  //该项将在遵守给定约束的情况下尽可能宽（可拉伸）
        Layout.alignment: Qt.AlignBottom //标注图位于顶部
        id:tag_view
        height: 120  //标注 坐标轴高度

    } 
    Connections {
        target: page_viewmodel //联系 目标
        function onCanvasInvalidated() {
            tag_view.update()
        }
    }


}
