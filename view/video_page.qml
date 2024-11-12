import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    RowLayout {
        ToolButton {
            text: "视频"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/video2.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                window_loader.setSource("video_property_view.qml",{"viewmodel":contentLoader.item.viewmodel})
            }
        }
        ToolButton {
            text: "属性"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/设置.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
                contentLoader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
            }
        }
        ToolButton {
            text: "放大镜"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/放大.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.maggot_mode = !contentLoader.item.viewmodel.maggot_mode
            }
        }
    }

}
