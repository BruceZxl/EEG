import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel

    ToolButton {
        text: "帮助"
        implicitWidth: 70
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/帮助.jpg"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }
    ToolSeparator { Layout.fillHeight: true }
    ToolButton {
        text: "内容"
        implicitWidth: 70
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/filter.png"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }
    ToolButton {
        text: "索引"
        implicitWidth: 70
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/filter.png"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.maggot_mode = !main_loader.item.viewmodel.maggot_mode
        }
    }
    ToolButton {
        text: "查询"
        implicitWidth: 70
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/filter.png"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }
    ToolSeparator { Layout.fillHeight: true }
    ToolButton {
        text: "关于"
        implicitWidth: 70
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/filter.png"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }
    ToolSeparator { Layout.fillHeight: true }
    ToolButton {
        text: "compumedics互联网协助登录界面"
        implicitWidth: 210
        implicitHeight: 70
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/互联网帮助.jpg"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: {
            main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }


}