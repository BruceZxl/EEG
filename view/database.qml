import QtQuick
import QtQuick.Controls
import QtQuick.Layouts


RowLayout {


    ToolButton {
        text: "数据库连接"
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/database.jpg"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        // 在您的 ToolButton 点击事件槽函数中：
        onClicked: {
            dialog.x = (parent.width - dialog.width) / 2
            dialog.y = (parent.height - dialog.height) / 2
            dialog.visible = true
        }

    }
    Dialog {
            id: dialog
            title: "数据库连接"
            modal: true // 使对话框成为模态对话框
            contentItem: ColumnLayout {
                TextField {
                    id: ipField
                    placeholderText: "IP地址"
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                TextField {
                    id: portField
                    placeholderText: "端口"
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                TextField {
                    id: accountField
                    placeholderText: "账户"
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                TextField {
                    id: passwordField
                    placeholderText: "密码"
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                }
                Button {
                    text: "登录"
                    Layout.fillWidth: true
                    Layout.alignment: Qt.AlignHCenter
                    onClicked: {
                        // 在这里编写登录操作的逻辑
                        console.log("IP地址: " + ipField.text + ", 端口: " + portField.text + ", 账户: " + accountField.text + ", 密码: " + passwordField.text)
                        dialog.close()
                    }
                }
            }
        }



    ToolSeparator { Layout.fillHeight: true }
    ToolButton {
        text: "增加数据"
        display: AbstractButton.TextUnderIcon
        icon.source: "images/icon/add1.png"
        icon.color: "transparent"
        icon.width: 40 // 设置图标宽度为40
        icon.height: 40 // 设置图标高度为40
        onClicked: contentLoader.setSource("")
    }




    ToolSeparator { Layout.fillHeight: true }
    ToolButton {
            text: "删除数据"
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/delete1.png"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: contentLoader.setSource("")
        }

    ToolSeparator { Layout.fillHeight: true }


    ToolButton {
                text: "修改数据"
                display: AbstractButton.TextUnderIcon
                icon.source: "images/icon/修改.png"
                icon.color: "transparent"
                icon.width: 40 // 设置图标宽度为40
                icon.height: 40 // 设置图标高度为40
                onClicked: contentLoader.setSource("")
            }
    ToolSeparator { Layout.fillHeight: true }


// 右部分使用Loader来加载RightPanel.qml
    Loader {
        id: rightPanelLoader
        width: 200 // 或者根据需要设置宽度
        height: parent.height
        source: "finddata.qml" // 指定要加载的QML文件路径
    }
    ToolSeparator { Layout.fillHeight: true }

}
