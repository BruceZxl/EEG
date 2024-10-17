import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import WaveformPageViewModel

Window{
    id: root
    title:"工程属性"
    width: 170
    height: 220
    visible: true
    color: "white"
    ColumnLayout{
    property WaveformPageViewModel viewmodel: parent.viewmodel
    property string path
    id:channelproperty
    Layout.fillHeight: true
    Layout.fillWidth: true
    Text {
            x:0
            y:0
            text: "文件位置: " + channelproperty.path // 显示文件路径
            font.pixelSize: 16 // 设置字体大小
            color: "black" // 设置文本颜色为黑色
            anchors.centerIn: parent // 在父容器中居中显示
        }
    }

}
