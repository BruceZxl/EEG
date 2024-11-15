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
        width: 200 // 设置按钮宽度
        height: 80 // 设置按钮高度
        font.pixelSize: 20 // 设置字体大小
        font.family: "Arial" // 设置字体类型
        onClicked: {
            if(channel_area.visible == false){
                channel_area.visible = true
                //channel_window.visible = true
                channel_loader.setSource("channel_property_view.qml",{"viewmodel":contentLoader.item.viewmodel})
                contentLoader.item.viewmodel.position_mode = true

            }

            else{
                channel_area.visible = false
                //channel_window.visible = false
                channel_loader.source = ""
            }
            //button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[0])
        }
    }

    Button {
        text: "工程属性"
        width: 200
        height: 80
        font.pixelSize: 20
        font.family: "Arial"
        onClicked: {
            if(engineering_area.visible == false){
                engineering_area.visible = true
                //engineering_window.visible = true
                engineering_loader.setSource("engineering_property_view.qml",{"viewmodel":contentLoader.item.viewmodel,"path":folderDialog.file})
            }
            else{
                //engineering_window.visible = false
                engineering_area.visible = false
                engineering_loader.source = ""
            }
            //button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[1])
        }
    }

    Button {
        text: "视频同步"
        width: 200
        height: 80
        font.pixelSize: 20
        font.family: "Arial"
        onClicked: {
             onClicked: {
                console.log("video_window visible: ", video_window.visible)
                console.log("contentLoader item: ", contentLoader.item)
                console.log("viewmodel: ", contentLoader.item ? contentLoader.item.viewmodel : "null")

                if (video_window.visible == false) {
                    video_window.visible = true
                    video_loader.source = "video_property_view.qml"
                    if (video_loader.item) {
                        video_loader.item.viewmodel = contentLoader.item.viewmodel
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

