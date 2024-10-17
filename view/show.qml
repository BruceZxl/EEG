import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout{
    //显示
    id:button_layout
    Layout.fillHeight: true
    property int current_index:0
    property var button_index: [1,2,3]
    Layout.preferredWidth: 100
    spacing:20

    function updata_index(current_index,button_index) {
        if (current_index == button_index) return 0
        else {

            return button_index
        }
    }

    Button {
        text: "通道属性"
        width: 150 // 设置按钮宽度
        height: 50 // 设置按钮高度
        font.pixelSize: 16 // 设置字体大小
        font.family: "Arial" // 设置字体类型
        onClicked: {
            if(channel_window.visible == false){
                channel_window.visible = true
                channel_loader.setSource("channel_property_view.qml",{"viewmodel":main_loader.item.viewmodel})
                main_loader.item.viewmodel.position_mode = true

            }

            else{
                channel_window.visible = false
                channel_loader.source = ""
            }
            //button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[0])
        }
    }

    Button {
        text: "工程属性"
        width: 150
        height: 50
        font.pixelSize: 16
        font.family: "Arial"
        onClicked: {
            if(engineering_window.visible == false){
                engineering_window.visible = true
                engineering_loader.setSource("engineering_property_view.qml",{"viewmodel":main_loader.item.viewmodel,"path":folderDialog.file})
            }
            else{
                engineering_window.visible = false
                engineering_loader.source = ""
            }
            //button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[1])
        }
    }

    Button {
        text: "视频同步"
        width: 150
        height: 50
        font.pixelSize: 16
        font.family: "Arial"
        onClicked: {
             onClicked: {
                console.log("video_window visible: ", video_window.visible)
                console.log("main_loader item: ", main_loader.item)
                console.log("viewmodel: ", main_loader.item ? main_loader.item.viewmodel : "null")

                if (video_window.visible == false) {
                    video_window.visible = true
                    video_loader.source = "video_property_view.qml"
                    if (video_loader.item) {
                        video_loader.item.viewmodel = main_loader.item.viewmodel
                    } else {
                        console.log("Error: video_loader item is null")
                    }
                } else {
                    video_window.visible = false
                    video_loader.source = ""
                }
            }
            //button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[2])
        }
    }


}

