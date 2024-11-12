import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
    property WaveformPageViewModel viewmodel: parent.viewmodel
    Label {  //标签 帧大小
            text: "纺锤波标注" //帧大小标签
        }
    ColumnLayout{
        Button {
            text: "纺锤波"
            Layout.fillWidth: true
            Layout.preferredWidth: 50
            onClicked:function(mouse){
                   contentLoader.item.viewmodel.mark_spindle_notation_num = 1;

            }
            background: Rectangle {
                color: "yellow"
                opacity: 0.6
            }
        }

    }
    ColumnLayout{
        Button {
            text: "自动标注"
            Layout.fillWidth: true
            Layout.preferredWidth: 100
            onClicked:{
                contentLoader.item.viewmodel.auto_spindle_annotate_flag = 1
            }
        }

        Button {
            text: "确定/保存"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                contentLoader.item.viewmodel.set_save_flag_spindle = 1
            }
        }

        Button {
            text: "删除"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                contentLoader.item.viewmodel.set_delete_flag_spindle = 1
            }
        }

        Button {
            text: "保存到数据库"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                contentLoader.item.viewmodel.save_mark_breathe_event_record = 1
            }
        }
    }


}


