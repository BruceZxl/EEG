import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    // 滤波参数输入框
    ColumnLayout {
        Layout.leftMargin: 20
            RowLayout{
            ColumnLayout{
                TextArea {
                id: highpass_filter_input
                implicitWidth: 100
                placeholderText: qsTr("高通滤波")
                }
                TextArea {
                    id: lowpass_filter_input
                    implicitWidth: 100
                    placeholderText: qsTr("低通滤波")
                }
                }
                ToolButton {
                    text: "滤波"
                    implicitWidth: 70
                    implicitHeight: 50
                    display: AbstractButton.TextUnderIcon
                    icon.source: "images/icon/filter.png"
                    icon.color: "transparent"
                    onClicked: {
                        main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
                        main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
                    }
                }
        }

        RowLayout {
            Text {
                text: "    工频滤波"
            }
            ComboBox {
                id: filterComboBox
                model: ["None", "50Hz", "60Hz"] // 滤波参数列表
                onActivated: {
                    if (filterComboBox.currentText === "50Hz") {
                        main_loader.item.viewmodel.notch = parseFloat(50) || 0
                    } else if (filterComboBox.currentText === "60Hz") {
                        main_loader.item.viewmodel.notch = parseFloat(60) || 0
                    } else {
                        main_loader.item.viewmodel.notch = 0
                    }
                }
            }
        }


    }
}