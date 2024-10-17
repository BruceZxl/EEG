import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import WaveformPageViewModel


ColumnLayout{
    property WaveformPageViewModel viewmodel: parent.viewmodel
    property string path
    id:channelproperty
    Layout.fillHeight: true
    Layout.fillWidth: true
    Text{
            x:0
            y:0
            text:"文件位置:" + path
            width: parent.width
            height: parent.height
            
        }
}
