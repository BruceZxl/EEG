import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import WaveformAreaViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    // 滤波参数输入框
    ColumnLayout {
        Layout.leftMargin: 20
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
    Button {
        text: "滤波"
        implicitWidth: 70
        implicitHeight: 50
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/filter.png"
        icon.color: "transparent"
        onClicked: {
            contentLoader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
            contentLoader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
        }
    }
    ColumnLayout {
        RowLayout {
            Text { text: "工频滤波" }
            ComboBox { model: ["暂不可用"] }
        }
        // Montage
        RowLayout {
            Text { text: "Montage" }
            ComboBox {
                model: MontageRegistry.get_names()
                currentIndex: contentLoader.item?.viewmodel.montage_index ?? 0
                implicitWidth: 100
                onActivated: function (index) {
                    contentLoader.item.viewmodel.montage_index = index
                }
            }
        }

        RowLayout {
            Text { text: "参考" }
            ComboBox {
               model: 25
                onActivated: function (index) {
                    contentLoader.item.viewmodel.reference = index
                }
               }
        }
    }
    // 标注
    ColumnLayout{
        RowLayout{
            Layout.margins: 5
            Button {
                text: "标注"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked: {
                    if(mark_loader.source != ""){
                        mark_loader.source = ""
                        mark_loader.visible=false
                    }
                    else {
                        mark_loader.visible=true
                        mark_loader.setSource("tag_view.qml",{"page_viewmodel":contentLoader.item.viewmodel});
                        contentLoader.item.viewmodel.seek(0)
                    }
                }
            }
            Button {
                text: "N1"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='N1'
                }
            }
            Button {
                text: "N2"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='N2'
                }
            }
            Button {
                text: "N3"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='N3'
                }
            }
            GroupBox {
                background: Rectangle { color: "transparent" }
                RowLayout {
                    RadioButton {
                        checked: true
                        text: qsTr("算法1")
                    }
                    RadioButton {
                        checked: false
                        text: qsTr("算法2")
                    }
                }
            }
        }
        RowLayout {
            Layout.margins: 5
            Button {
                text: "W"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='W'
                }
            }
            Button {
                text: "R"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='R'
                }

            }
            Button {
                text: "?"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.mark_sequence='?'
                }

            }
            Button {
                text: "<"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    if(contentLoader.item.viewmodel.position!=0) contentLoader.item.viewmodel.seek(contentLoader.item.viewmodel.position-30)
                }
            }
            Button {
                text: ">"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.seek(contentLoader.item.viewmodel.position+30)
                }
            }


            Button {
                text: "保存"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    contentLoader.item.viewmodel.save_mark_sequence='1'
                }
            }
        }
    }
}   