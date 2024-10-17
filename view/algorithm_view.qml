import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import WaveformPageViewModel
import MontageRegistry

RowLayout {
// 标注
//     height:100
    ColumnLayout{
        RowLayout{
            Layout.margins: 5
            Button {
                text: "标注"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked: {
                    if(mark_loader.source != ""){
                        mark_loader.source = ""
                        mark_loader.visible=false
                    }
                    else {
                        mark_loader.visible=true
                        mark_loader.setSource("tag_view.qml",{"page_viewmodel":main_loader.item.viewmodel});
                        main_loader.item.viewmodel.seek(0)
                    }
                }
            }
            Button {
                text: "N1"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='N1'
                }
            }
            Button {
                text: "N2"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='N2'
                }
            }
            Button {
                text: "N3"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='N3'
                }
            }
            GroupBox {
                background: Rectangle { color: "transparent" }
                RowLayout {
                    RadioButton {
                        checked: true
                        text: qsTr("算法1")
                    }
                    RadioButton {
                        checked: false
                        text: qsTr("算法2")
                    }
                }
            }
        }
        RowLayout {
            Layout.margins: 5
            Button {
                text: "W"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='W'
                }
            }
            Button {
                text: "R"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='R'
                }

            }
            Button {
                text: "?"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.mark_sequence='?'
                }

            }
            Button {
                text: "<"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    if(main_loader.item.viewmodel.position!=0) main_loader.item.viewmodel.seek(main_loader.item.viewmodel.position-30)
                }
            }
            Button {
                text: ">"
                Layout.fillWidth: true
                Layout.preferredWidth: 50
                onClicked:{
                    main_loader.item.viewmodel.seek(main_loader.item.viewmodel.position+30)
                }
            }
        }
    }
        ToolSeparator { Layout.fillHeight: true }
            // Montage
    RowLayout {
        Text { text: "Montage" }
        ComboBox {
            model: MontageRegistry.get_names()
            currentIndex: main_loader.item?.viewmodel.montage_index ?? 0
            implicitWidth: 100
            onActivated: function (index) {
                main_loader.item.viewmodel.montage_index = index
            }
        }
    }
    ToolSeparator { Layout.fillHeight: true }
    Loader {
        id: rightPanelLoaderAlgorithm
        width: 200 // 或者根据需要设置宽度
        height: parent.height
        source: "filter.qml" // 指定要加载的QML文件路径
    }
    ToolSeparator { Layout.fillHeight: true }
    Loader {
        id: rightPanelLoaderBreathAlgorithm
        width: 200 // 或者根据需要设置宽度
        height: 600
        source: "algorithm/breath_event.qml" // 指定要加载的QML文件路径
    }
    ToolSeparator { Layout.fillHeight: true }

    Loader {
            id: rightPanelLoaderBreathAlgorithm1
            width: 200 // 或者根据需要设置宽度
            height: 600
            source: "algorithm/spindle_notation.qml" // 指定要加载的QML文件路径
        }

    ToolSeparator { Layout.fillHeight: true }
    // 工具按钮，打开算法选择窗口
        ToolButton {
            text: "算法选择"
            implicitWidth: 70
            implicitHeight: 70
            display: AbstractButton.TextUnderIcon
            icon.source: "images/icon/video2.jpg"
            icon.color: "transparent"
            icon.width: 40 // 设置图标宽度为40
            icon.height: 40 // 设置图标高度为40
            onClicked: {
                windowLoader.setSource("algorithm_window.qml")
            }
        }
         // 用于加载其他窗口的 Loader
        Loader {
            id: windowLoader
            width: 200 // 或者根据需要设置宽度
            height: parent.height
        }
}