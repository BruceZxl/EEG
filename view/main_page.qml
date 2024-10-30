import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import OSColors
//import WaveformView
//import WindowHeight

ApplicationWindow {
    visible: true
    width: 1400
    height: 750
    title: "EEG工具箱"

    SystemPalette {
        id: activePalette
        colorGroup: SystemPalette.Active
    }
    header: ToolBar {
        horizontalPadding: 0
        ColumnLayout {
            anchors.fill: parent
            spacing: 0
            RowLayout {
            Layout.fillWidth: true
                id: menu_window
                property Item current: null
                readonly property int button_width: 80
                height: 60
                spacing: 0

                ToolButton {
                    text: "回顾"
                    checkable: true
                    checked: { menu_window.current == this }
                    contentItem: Text {
                        text: parent.text
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        // color: { OSColors.is_accent_dark() ? "white" : "black" }
                    }
                    implicitWidth: menu_window.button_width
                    Layout.fillHeight: true
                    property HoverHandler hoverHandler: null
                    HoverHandler {
                        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                        Component.onCompleted: parent.hoverHandler = this
                    }

                    onClicked: {
                        if (menu_window.current != this) {
                            context_loader.setSource("open_menu.qml")
                            menu_window.current = this
                        } else {
                            context_loader.setSource("")
                            menu_window.current = null
                        }
                    }
                }

                ToolButton {
                    text: "算法"
                    implicitWidth: menu_window.button_width
                    Layout.fillHeight: true
                    checkable: true
                    checked: { menu_window.current == this }
                    // enabled: main_loader.item != null
                    onClicked: {
                        if (menu_window.current != this) {
                            context_loader.setSource("algorithm_view.qml", {
                                "viewmodel": contentLoader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            context_loader.setSource("")
                            menu_window.current = null
                        }
                    }
                }
                ToolButton {
                    text: "报告"
                    implicitWidth: menu_window.button_width
                    Layout.fillHeight: true
                    checkable: true
                    checked: { menu_window.current == this }
                    // enabled: contentLoader.item != null
                    onClicked: {
                        if (menu_window.current != this) {
                            context_loader.setSource("report_view.qml", {
                                "viewmodel": contentLoader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            context_loader.setSource("")
                            menu_window.current = null
                        }
                    }
                }
                ToolButton{
                    text: "显示"
                    implicitWidth: menu_window.button_width
                    Layout.fillHeight: true
                    checkable: true
                    checked: { menu_window.current == this }
                    onClicked: {
                        if(menu_window.current != this) {
                            context_loader.setSource("show.qml", {
                                "viewmodel": contentLoader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            context_loader.setSource("")
                            menu_window.current = null
                        }
                    }
                }

                ToolButton {
                    text: "帮助"
                    implicitWidth: menu_window.button_width
                    Layout.fillHeight: true
                    checkable: true
                    checked: { menu_window.current == this }
                    onClicked: {
                        if (menu_window.current != this){
                            context_loader.setSource("help_view.qml")
                            menu_window.current = this
                        }
                        else{
                            context_loader.setSource("")
                            menu_window.current = null
                        }

                    }
                }
                ToolButton {
                    implicitWidth: menu_window.button_width * 1.4
                    Layout.fillHeight: true
                    property int benchmark_result: -1
                    text: ((benchmark_result > 0) ? `（FPS: ${benchmark_result}）` : "性能测试 ")
                    onClicked: {
                        if (contentLoader.source == "") {
                            contentLoader.setSource("waveform_page.qml", {"loadSine": true})

                        }
                        benchmark_result = contentLoader.item?.tess(50) ?? -1
                    }
                }

                ToolButton {
                    implicitWidth: menu_window.button_width * 1.4
                    Layout.fillHeight: true
                    text: ("结构图")
                    onClicked: {
                        if (!structure_area.visible) {
                            //structure_loader.setSource("") //装载时启用
                            structure_area.visible = true
                        }
                        else{
                            //structure_loader.setSource("")
                            structure_area.visible = false
                        }
                    }
                }
            }

            FolderDialog {
                id: importToDialog
                title: "Save imported project to..."
                onAccepted: contentLoader.setSource("waveform_page.qml", {
                    "path": folder,
                    "importFrom": importFileDialog.file,
                    "importFormat": importFileDialog.lastSelectedExtension
                })
            }

            FolderDialog {
                id: folderDialog
                title: "Select project"
                onAccepted: contentLoader.setSource("waveform_page.qml", {"path": folder})
            }

            FileDialog {
                id: importFileDialog
                title: "Import..."
                property string lastSelectedExtension: selectedNameFilter.extensions[0]
                onAccepted: importToDialog.open()
                nameFilters: ["edf/edf+ (*.edf)", "bdf/bdf+ (*.bdf)"]
            }

            FolderDialog {
                id: createNewDialog
                title: "Save new project to..."
                onAccepted: main_loader.setSource("waveform_page.qml", {
                    "path": folder,
                    "neo": true
                })
            }
        }
    }
    ColumnLayout {
        id: context_area
        anchors.fill: parent

        // 上下文区域，固定高度120
        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            visible: context_loader.source != ""// 当source不为空时可见
            Rectangle {
                anchors.fill: parent
                color: "lightblue" // 背景颜色填充整个区域
            }

            Loader {
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 30 // 左边距
                anchors.rightMargin: 30 // 右边距
                id: context_loader
                source: "" // 设置为非空字符串以加载内容
            }
            Rectangle {
                    color: "transparent" // 确保内部颜色不覆盖背景
                    anchors.fill: parent
                    /*Text {
                        anchors.centerIn: parent
                        text: "上下文内容"
                    }*/
                }
        }



        // 使用Splitter来分隔第二块和第三块
        SplitView {
            orientation: Qt.Vertical
            Layout.fillWidth: true
            Layout.fillHeight: true

            // 结构区
            Item {
                id: structure_area
                Layout.fillWidth: true
                SplitView.preferredHeight: 150 // 启动时高度为150
                SplitView.minimumHeight: 100
                visible: structure_loader.source != "" // 当source不为空时可见
                Rectangle {
                    anchors.fill: parent
                    color: "lightgreen" // 背景颜色填充整个区域
                    Text {
                        anchors.centerIn: parent
                        text: "结构图"
                    }
                }

                Loader {
                    anchors.fill: parent
                    id: structure_loader//结构图
                    source: "" // 设置为非空字符串以加载内容

                    Rectangle {
                        anchors.fill: parent
                        color: "transparent" // 确保内部颜色不覆盖背景
                        /*Text {
                            anchors.centerIn: parent
                            text: "结构区"
                        }*/
                    }
                }
            }

            // 第三块，分为左右两部分
            SplitView {
                orientation: Qt.Horizontal
                Layout.fillWidth: true
                Layout.fillHeight: true
                SplitView.preferredHeight: 600 // 设置启动时的首选高度
                SplitView.minimumHeight: 600 // 设置最小高度

                // 左半区，信息显示区，分为上下两部分
                SplitView {
                    orientation: Qt.Vertical
                    //SplitView.fillWidth: true
                    SplitView.preferredWidth: 300 // 设置初始宽度
                    SplitView.minimumWidth: 200 // 设置最小宽度

                    //visible: false

                    // 通道属性
                    Item {
                        id: channel_area
                        SplitView.fillWidth: true
                        SplitView.preferredHeight: 300 // 设置启动时的首选高度
                        SplitView.minimumHeight: 200 // 设置最小高度
                        visible: structure_loader.source != "" // 当source不为空时可见
                        Rectangle {
                            anchors.fill: parent
                            color: "#B0C4DE" // 浅蓝灰
                            /*Text {
                                anchors.centerIn: parent
                                text: "通道属性"
                            }*/
                        }
                        Loader {
                            anchors.top: parent.top // 上对齐
                            anchors.left: parent.left // 左对齐
                            anchors.margins: 50 // 设置上边距为50
                            scale: 1.3
                            id: channel_loader
                            source: "" // 设置为非空字符串以加载内容

                            Rectangle {
                                anchors.fill: parent
                                color: "transparent" // 确保内部颜色不覆盖背景
                            }
                        }
                    }

                    // 工程属性
                    Item {
                        id: engineering_area
                        Layout.fillWidth: true
                        SplitView.preferredHeight: 200 // 设置启动时的首选高度
                        SplitView.minimumHeight: 200 // 设置最小高度
                        visible: structure_loader.source != "" // 当source不为空时可见
                        Rectangle {
                            anchors.fill: parent
                            color: "#B0C4DE" // 浅蓝灰
                            /*Text {
                                anchors.centerIn: parent
                                text: "工程属性"
                            }*/
                        }
                        Loader {
                            anchors.top: parent.top // 上对齐
                            anchors.left: parent.left // 左对齐
                            anchors.margins: 50 // 设置上边距为50
                            scale: 1.3
                            id: engineering_loader
                            source: "" // 设置为非空字符串以加载内容

                            Rectangle {
                                anchors.fill: parent
                                color: "transparent" // 确保内部颜色不覆盖背景
                            }
                        }
                    }
                }
                 // 右半区，主界面
                Rectangle {
                    SplitView.fillWidth: true
                    SplitView.minimumWidth: 800 // 设置最小宽度
                    color: "white"
                    Text {
                        anchors.centerIn: parent
                        text: "主界面"
                    }
                    Loader {
                        id: contentLoader
                        anchors.fill: parent

                        onHeightChanged: WaveformView.setWindowHeight(height)
                    }

                }
            }

        }
    }
    Item {
        anchors.fill: parent
        id: body
        property bool loading

        U.ProgressBar {
            indeterminate: true
            anchors.left: parent.left
            anchors.right: parent.right
            visible: body.loading
        }

        /*ApplicationWindow {
            id: channel_window
            visible: false // 初始状态为隐藏
            width: 400
            height: 300
            title: "通道属性"

            // 设置窗口为无边框
            flags: Qt.Window | Qt.FramelessWindowHint

            Loader {
                id: channel_loader
                source: ""
                visible: source != ""
                active: channel_loader.visible
                Layout.preferredWidth: 100
                Layout.fillHeight: true
            }
        }*/

         /*ApplicationWindow {
            id: engineering_window
            visible: false // 初始状态为隐藏
            width: 400
            height: 300
            title: "工程属性"

            // 设置窗口为无边框
            flags: Qt.Window | Qt.FramelessWindowHint

            Loader {
                id: engineering_loader
                source: ""
                visible: source != ""
                active: engineering_loader.visible
                Layout.preferredWidth: 100
                Layout.fillHeight: true
            }
        }*/

        ApplicationWindow {
            id: video_window
            title:"视频同步"
            width: 170
            height: 220
            visible: false
            //color: "white"

            // 设置窗口为无边框
            flags: Qt.Window | Qt.FramelessWindowHint


            Loader {
                id: video_loader
                source: ""
                visible: source != ""
                active: video_loader.visible
                Layout.preferredWidth: 100
                Layout.fillHeight: true
            }
        }

        /*ApplicationWindow {

            visible: false
            width: 800
            height: 600
            title: "主工作区"
            Item {
                anchors.fill: parent
                id: wbody
                property bool loading

                U.ProgressBar {
                    indeterminate: true
                    anchors.left: parent.left
                    anchors.right: parent.right
                    visible: wbody.loading
                }

                Loader {
                            active: source != ""
                            id: main_loader1
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                    }
            }
        }*/



        ColumnLayout {
            anchors.fill: parent
            
            Loader {
                active: source != ""
                id: mark_loader
                visible:false
                Layout.fillWidth: true
                Layout.fillHeight: true
                Layout.preferredHeight: 80
            }

            RowLayout{




                Loader {
                        active: source != ""
                        id: main_loader
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                }

            }

            Loader {
                source: ""
                visible: source != ""
                id: ipwin_loader
                Layout.preferredWidth: 150
                Layout.fillWidth: true
                Layout.fillHeight: true
            }


            Loader {
                id: ipport_window
                active: main_loader.item?.viewmodel.ipport_mode ?? false
                source: "ipport_view.qml"
            }

            Connections {
                target: ipport_window.item?.window ?? null
                function onClosing(val) {
                    main_loader.item.viewmodel.ipport_mode = false
                }
            }

            Connections {
                target: main_loader.item?.viewmodel ?? null
                function onLoadingChanged(val) {
                    body.loading = val
                }
            }
        }

    }
}
