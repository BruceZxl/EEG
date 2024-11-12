import QtQuick 2.2
import QtQuick.Window 2.2
import QtQuick.Controls
import QtQuick.Layouts
import WaveformPageViewModel
Rectangle{
    visible:true
    ToolBar {
    RowLayout {
        height:50
        anchors.fill: parent
        ToolButton {
            height:50
            text: qsTr("打开文件")
            onClicked:{
                if(menuWindow.current_index != menuWindow.button_index[0]){
                    menuWindow.tempColor=open.color
                    open.color=openText.color
                    openText.color=menuWindow.tempColor
                    menu_view_loader.setSource("open_menu.qml")
                    console.log("menuWindow.current_index",menuWindow.current_index)
                }
                menuWindow.current_index = menuWindow.updata_index(menuWindow.current_index,menuWindow.button_index[0])
                console.log("menuWindow.current_index",menuWindow.current_index)
                }
        }

        ToolButton {
            text: qsTr("滤波")
            onClicked:{
                if(menuWindow.current_index != menuWindow.button_index[2]){
                    filter.color="aliceblue"
                    filterText.color="steelblue"
                    menu_view_loader.setSource("filter_menu.qml",{"viewmodel":contentLoader.item.viewmodel,"isVisiable":true})
                    console.log("menuWindow.current_index",menuWindow.current_index)
                }else{
                    filter.color="steelblue"
                    menu_view_loader.setSource("")
                }
            menuWindow.current_index = menuWindow.updata_index(menuWindow.current_index,menuWindow.button_index[2])
            }
        }
        ToolButton {
            text: qsTr("拓展")
        }
//        ToolButton {
//            text: qsTr("2")
//        }
    }
}
}