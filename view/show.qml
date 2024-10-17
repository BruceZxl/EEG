import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout{
    //显示

    Button {
        text: "通道属性"
        onClicked:{

            if(button_layout.current_index != button_layout.button_index[0]){
                window_loader.setSource("channel_property_view.qml",{"viewmodel":main_loader.item.viewmodel})
                main_loader.item.viewmodel.position_mode = true
            }
            else{
                window_loader.source = ""
            }
            button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[0])
        }
    }
    Button {
        text: "工程属性"
        onClicked:{

            if(button_layout.current_index != button_layout.button_index[1]){
                window_loader.setSource("engineering_property_view.qml",{"viewmodel":main_loader.item.viewmodel,"path":folderDialog.file})
            }
            else{
                window_loader.source = ""
            }
            button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[1])
            }
    }

    Button {
        text: "视频同步"
        onClicked:{
            if(button_layout.current_index != button_layout.button_index[2]){
                window_loader.setSource("video_property_view.qml",{"viewmodel":main_loader.item.viewmodel})
            }
            else{
                window_loader.source = ""
            }
            button_layout.current_index = button_layout.updata_index(button_layout.current_index,button_layout.button_index[2])
            }
    }


}

