import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    // 数据库查找
    ColumnLayout {
        Layout.leftMargin: 30
        RowLayout {
            Text {
                text: "查找类型:"
            }
            ComboBox {
                id: filterComboBox
                model: ["None","模糊查询", "标签查询", "全字段查询"] // 滤波参数列表
                onActivated: {
                    if (filterComboBox.currentText === "模糊查询") {
                        main_loader.item.viewmodel.notch = parseFloat(50) || 0
                    } else if (filterComboBox.currentText === "标签查询") {
                        main_loader.item.viewmodel.notch = parseFloat(60) || 0
                    } else {
                        main_loader.item.viewmodel.notch = 0
                    }
                }
            }
        }

        RowLayout{
        ColumnLayout{
            TextArea {
            id: highpass_filter_input
            implicitWidth: 90
            placeholderText: qsTr("查询数据")
            }
            }
            ToolButton {
                text: "查询"
                implicitWidth: 60
                implicitHeight: 35
                display: AbstractButton.TextUnderIcon
                icon.source: "images/icon/query.png"
                icon.color: "transparent"
                onClicked: {
                    main_loader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
                    main_loader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
                }
            }
        }
    }
}