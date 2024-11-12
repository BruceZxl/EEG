import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


RowLayout {

    // ToolButton {
    //     text: "打开文件"
    //     display: AbstractButton.TextUnderIcon
    //     icon.source: "images/icon/open.png"
    //     icon.color: "transparent"
    //     onClicked: folderDialog.open()
    // }
    ToolButton {
        text: "打开文件"//原EDF导入
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/打开文件.jpg"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: importFileDialog.open()
    }
    ToolButton {
        text: "关闭文件"
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/删除.jpg"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: contentLoader.setSource("")
    }
    ToolSeparator { Layout.fillHeight: true }
    // ToolButton {
    //     text: "新建空白"
    //     display: AbstractButton.TextUnderIcon
    //
    //     icon.source: "images/icon/create_blank.png"
    //     icon.color: "transparent"
    //     onClicked: createNewDialog.open()
    // }
    // ToolButton {
    //     text: "添加数据(实例)"
    //     display: AbstractButton.TextUnderIcon
    //     icon.source: "images/icon/append_data.png"
    //     icon.color: "transparent"
    //     onClicked: contentLoader.item.viewmodel.append_example()
    // }
    // ToolButton {
    //     text: "保存变更"
    //     display: AbstractButton.TextUnderIcon
    //     icon.source: "images/icon/save_change.png"
    //     icon.color: "transparent"
    //     onClicked: contentLoader.item.viewmodel.save_changes()
    // }
    // ToolButton {
    //     text: "接收数据开关"
    //     display: AbstractButton.TextUnderIcon
    //     icon.source: "images/icon/save_change.png"
    //     icon.color: "transparent"
    //     onClicked: ipwin_loader.setSource("ipport_view.qml", {"viewmodel": contentLoader.item.viewmodel})
    // }
    // ToolSeparator { Layout.fillHeight: true }
    // ToolButton {
    //     text: "sine"
    //     display: AbstractButton.TextUnderIcon
    //     icon.source: "images/icon/sin.png"
    //     icon.color: "transparent"
    //     onClicked: contentLoader.setSource("waveform_page.qml", {"loadSine": true})
    // }

    ColumnLayout {
    spacing: 2 // RowLayout之间的垂直间距

    RowLayout {
        spacing: 2 // 文本和按钮之间的水平间距
        Button {
        id: myButton
        text: "保存"
        contentItem: RowLayout {
            spacing: 10
            Rectangle {
                width: 15
                height: 15
                color: "transparent" // 设置透明背景

                Image {
                    anchors.fill: parent
                    source: "images/icon/保存2.jpg"
                }
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
        text: "打印"
        contentItem: RowLayout {
            spacing: 10
             Rectangle {
                width: 15
                height: 15
                color: "transparent" // 设置透明背景

                Image {
                    anchors.fill: parent
                    source: "images/icon/打印.jpg"
                }
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

    RowLayout {
        spacing: 2 // 文本和按钮之间的水平间距
        Button {
        id: myButton3
        text: "打印设置"
        contentItem: RowLayout {
            spacing: 10

            Rectangle {
                width: 15
                height: 15
                color: "transparent" // 设置透明背景

                Image {
                    anchors.fill: parent
                    source: "images/icon/打印设置.jpg"
                }
            }

            Text {
                text: myButton3.text
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
// 右部分使用Loader来加载RightPanel.qml
    Loader {
        id: rightPanelLoader
        width: 200 // 或者根据需要设置宽度
        height: parent.height
        source: "filter.qml" // 指定要加载的QML文件路径
    }
    ToolSeparator { Layout.fillHeight: true }
    // 右部分使用Loader来加载RightPanel.qml
    Loader {
        id: rightPanelLoader2
        width: 200 // 或者根据需要设置宽度
        height: parent.height
        source: "video_page.qml" // 指定要加载的QML文件路径
    }
        ToolSeparator { Layout.fillHeight: true }

}
