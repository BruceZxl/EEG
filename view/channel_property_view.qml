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

            Column {
                anchors.fill: parent
                spacing: 5

                Text {
                    text: "通道名称:" + area_viewmodel.montage_block_viewmodel.channels[page_viewmodel.channel_index].name
                    width: 80
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideNone
                }

                Text {
                    text: "参考:" + area_viewmodel.montage_block_viewmodel.channels[page_viewmodel.reference].name
                    width: 80
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideNone
                }

                Text {
                    text: "高通滤波:" + page_viewmodel.hipass
                    width: channeLabelWidth
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideLeft
                }

                Text {
                    text: "低通滤波:" + page_viewmodel.lowpass
                    width: channeLabelWidth
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideMiddle
                }

                Text {
                    text: "放大倍数:" + page_viewmodel._user_amplifier
                    width: channeLabelWidth
                    font.pointSize: 10
                    color: "black"
                    elide: Text.ElideRight
                }

                Item {
                    width: 200
                    height: 100
                    Row {
                        Text {
                            text: "颜色："
                            font.pointSize: 10
                            color: "black"
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