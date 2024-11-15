import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import WaveformAreaViewModel
import WaveformView
import Qt.labs.qmlmodels


Repeater {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    id: areas
    model: viewmodel.area_viewmodels
    delegate: Column {
        anchors.fill: parent
        spacing: 10
        property WaveformPageViewModel page_viewmodel: viewmodel
        readonly property WaveformAreaViewModel area_viewmodel: modelData
        property string selectedColor: "#FFFFFF"
        readonly property int channeLabelWidth: 100

        Rectangle {
            anchors.fill: parent
            color: "transparent" // 确保背景是透明的，避免遮挡文本

            GridLayout {
                anchors.fill: parent
                columns: 3 // 增加一列用于放置垂直线条
                columnSpacing: 0
                rowSpacing: 0

                // 通道名称
                Text {
                    text: "通道名称:"
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                }
                Text {
                    text: area_viewmodel.montage_block_viewmodel.channels[page_viewmodel.channel_index].name
                    font.pointSize: 10
                    color: "black"
                }

                Rectangle {
                    height: 10
                    color: "black" // 使用黑色提高对比度
                    GridLayout.rowSpan: 1
                    GridLayout.columnSpan: 3
                }

                // 参考
                Text {
                    text: "参考:"
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                }
                Text {
                    text: area_viewmodel.montage_block_viewmodel.channels[page_viewmodel.reference].name
                    font.pointSize: 10
                    color: "black"
                }

                Rectangle {
                    height: 10
                    color: "black" // 使用黑色提高对比度
                    GridLayout.rowSpan: 1
                    GridLayout.columnSpan: 3
                }

                // 高通滤波
                Text {
                    text: "高通滤波:"
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                }
                Text {
                    text: page_viewmodel.hipass
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideLeft
                }

                Rectangle {
                    height: 10
                    color: "black" // 使用黑色提高对比度
                    GridLayout.rowSpan: 1
                    GridLayout.columnSpan: 3
                }

                // 低通滤波
                Text {
                    text: "低通滤波:"
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                }
                Text {
                    text: page_viewmodel.lowpass
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideMiddle
                }

                Rectangle {
                    height: 10
                    color: "black" // 使用黑色提高对比度
                    GridLayout.rowSpan: 1
                    GridLayout.columnSpan: 3
                }

                // 放大倍数
                Text {
                    text: "放大倍数:"
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                }
                Text {
                    text: page_viewmodel._user_amplifier
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideRight
                }

                Rectangle {
                    height: 10
                    color: "black" // 使用黑色提高对比度
                    GridLayout.rowSpan: 1
                    GridLayout.columnSpan: 3
                }

                // 颜色选择
                Text {
                    text: "颜色："
                    font.pointSize: 10
                    color: "black"
                }
                Rectangle {
                    width: 10
                    color: "black" // 使用黑色提高对比度
                    z:1
                }
                ComboBox {
                    id: colorComboBox
                    model: [
                        "#FF0000",
                        "#000000",
                        "#0000FF",
                        "#B8860B",
                        "#8B008B"
                    ]

                    onActivated: {
                        selectedColor = colorComboBox.model[colorComboBox.currentIndex]
                        console.log("Selected color: " + selectedColor)
                        page_viewmodel.colour_list = colorComboBox.currentIndex
                        console.log(page_viewmodel.colour_list)
                    }
                }
            }
        }
    }

    function judge_ref(string) {
        var index = -1
        var length = string.length
        index = string.indexOf('-')
        if (index == -1) {
            return 'None'
        } else {
            return string.substring(index + 1, length)
        }
    }
}