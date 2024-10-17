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
            text: "呼吸事件标注" //帧大小标签
        }
    ColumnLayout{
        Button {
            text: "中枢型呼吸事件"
            Layout.fillWidth: true
            Layout.preferredWidth: 50
            onClicked:function(mouse){
                   main_loader.item.viewmodel.mark_breathe_event_num = 0;

            }
            background: Rectangle {
                color: "red"
                opacity: 0.6
            }
        }
        Button {
            text: "阻塞型呼吸事件"
            Layout.fillWidth: true
            Layout.preferredWidth: 50
            onClicked:{
                main_loader.item.viewmodel.mark_breathe_event_num = 1;
            }
            background: Rectangle {
                color: "green"
                opacity: 0.6
            }
        }
        Button {
            text: "混合型呼吸事件"
            Layout.fillWidth: true
            Layout.preferredWidth: 100
            onClicked:{
                main_loader.item.viewmodel.mark_breathe_event_num = 2;
            }
            background: Rectangle {
                color: "blue"
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
                main_loader.item.viewmodel.auto_breathe_event_annotate_flag = 1
            }
        }

        Button {
            text: "确定/保存"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                main_loader.item.viewmodel.set_save_flag = 1
            }
        }

        Button {
            text: "删除"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                main_loader.item.viewmodel.set_delete_flag = 1
            }
        }

        Button {
            text: "保存到数据库"
            Layout.fillWidth: true
            Layout.preferredWidth: 30
            onClicked:{
                main_loader.item.viewmodel.save_mark_breathe_event_record = 1
            }
        }
    }


}


