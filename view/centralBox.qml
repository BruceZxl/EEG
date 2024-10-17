    // 左侧部分
    Item {
        Layout.fillWidth: true // 占据整个宽度
    }
    // 中间部分 - 方框
    Rectangle {
        width: 200  // 方框的宽度
        height: 200 // 方框的高度
        color: "lightgrey" // 方框的背景颜色
        border.color: "black" // 方框的边框颜色
        radius: 10 // 方框的圆角
        // 内部布局 - 垂直布局
        ColumnLayout {
            anchors.centerIn: parent // 居中
            Label {
                text: "IP:"
            }
            TextField {
                // IP 输入框
            }
            Label {
                text: "端口:"
            }
            TextField {
                // 端口输入框
            }
            Label {
                text: "用户名:"
            }
            TextField {
                // 用户名输入框
            }
            Label {
                text: "账号:"
            }
            TextField {
                // 账号输入框
            }
            Label {
                text: "密码:"
            }
            TextField {
                // 密码输入框
                echoMode: TextInput.Password // 以密码模式显示输入的字符
            }
        }
    }
    // 右侧部分
    Item {
        Layout.fillWidth: true // 占据整个宽度
    }
}