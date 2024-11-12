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
            text: "新建"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/创建报告.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
                contentLoader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
            }
        }
        ToolButton {
            text: "打开"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/打开文件.jpg"
            icon.color: "transparent"
            icon.width: 45 // 设置图标宽度为40
            icon.height: 45 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.lowpass = parseFloat(lowpass_filter_input.text) || 0
                contentLoader.item.viewmodel.hipass = parseFloat(highpass_filter_input.text) || 0
            }
        }
        ToolButton {
            text: "删除"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/删除.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.maggot_mode = !contentLoader.item.viewmodel.maggot_mode
            }
        }
        ToolButton {
            text: "输出"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/保存2.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                contentLoader.item.viewmodel.maggot_mode = !contentLoader.item.viewmodel.maggot_mode
            }
        }
        ToolSeparator { Layout.fillHeight: true }
        ColumnLayout{
            RowLayout {
                spacing: 2 // 文本和按钮之间的水平间距
                Button {
                id: myButton
                text: "报告"
                contentItem: RowLayout {
                spacing: 10
                Image {
                    id: buttonIcon
                    source: "path/to/your/报告.jpg" // 替换为你的图标路径
                    width: 30
                    height: 10
                }

                Text {
                    text: myButton.text
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                    font.pointSize: 8
                }
            }

            background: Rectangle {
                implicitWidth: 30
                implicitHeight: 8
                color: "#f0f0f0"
                radius: 5
            }
        }
}

            RowLayout {
            spacing: 2 // 文本和按钮之间的水平间距
            Button {
            id: myButton2
            text: "历史报告"
            contentItem: RowLayout {
                spacing: 8
                Image {
                    id: buttonIcon2
                    source: "path/to/your/icon.png" // 替换为你的图标路径
                    width: 30
                    height: 10
                }

                Text {
                    text: myButton2.text
                    verticalAlignment: Text.AlignVCenter
                    horizontalAlignment: Text.AlignLeft
                    font.pointSize: 8
                }
            }

            background: Rectangle {
                implicitWidth: 20
                implicitHeight: 8
                color: "#f0f0f0"
                radius: 5
            }
        }
        }
        }
        ToolSeparator { Layout.fillHeight: true }
            Loader {
                id: rightPanelLoader2
                width: 200 // 或者根据需要设置宽度
                height: parent.height
                source: "video_page.qml" // 指定要加载的QML文件路径
            }
    }

}
