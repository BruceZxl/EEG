import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import Qt.labs.platform
import QtQuick.Controls.Universal as U
import OSColors
import WaveformView

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
                    // background: Rectangle {
                    //     anchors.fill: parent
                    //     color: Qt.darker(
                    //         OSColors.accent(),
                    //         menu_window.current == parent ?
                    //             1.35 : parent.hoverHandler.hovered ? 1 : 1.2
                    //     )
                    // }
                    onClicked: {
                        if (menu_window.current != this) {
                            menu_view_loader.setSource("open_menu.qml")
                            menu_window.current = this
                        } else {
                            menu_view_loader.setSource("")
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
                            menu_view_loader.setSource("algorithm_view.qml", {
                                "viewmodel": main_loader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            menu_view_loader.setSource("")
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
                    // enabled: main_loader.item != null
                    onClicked: {
                        if (menu_window.current != this) {
                            menu_view_loader.setSource("report_view.qml", {
                                "viewmodel": main_loader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            menu_view_loader.setSource("")
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
                            menu_view_loader.setSource("show.qml", {
                                "viewmodel": main_loader.item.viewmodel
                            })
                            menu_window.current = this
                        } else{
                            menu_view_loader.setSource("")
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
                        menu_view_loader.setSource("help_view.qml")
                    }
                }
                ToolButton {
                    implicitWidth: menu_window.button_width * 1.4
                    Layout.fillHeight: true
                    property int benchmark_result: -1
                    text: ((benchmark_result > 0) ? `（FPS: ${benchmark_result}）` : "性能测试 ")
                    onClicked: {
                        if (main_loader.source == "") {
                            main_loader.setSource("waveform_page.qml", {"loadSine": true})
                            main_loader1.setSource("waveform_page.qml", {"loadSine": true})
                        }
                        benchmark_result = main_loader.item?.tess(50) ?? -1
                    }
                }
            }
            Item {
                Layout.fillWidth: true
                implicitHeight: 80
                visible: menu_view_loader.source != ""
                Loader {
                    id: menu_view_loader
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    source: ""
                    visible: source != ""
                }
            }
            
            FolderDialog {
                id: importToDialog
                title: "Save imported project to..."
                onAccepted: main_loader.setSource("waveform_page.qml", {
                    "path": folder,
                    "importFrom": importFileDialog.file,
                    "importFormat": importFileDialog.lastSelectedExtension
                })
            }

            FolderDialog {
                id: folderDialog
                title: "Select project"
                onAccepted: main_loader.setSource("waveform_page.qml", {"path": folder})
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


        ApplicationWindow {
            id: channel_window
            visible: false // 初始状态为隐藏
            width: 400
            height: 300
            title: "通道属性"

            Loader {
                id: channel_loader
                source: ""
                visible: source != ""
                active: channel_loader.visible
                Layout.preferredWidth: 100
                Layout.fillHeight: true
            }
        }

         ApplicationWindow {
            id: engineering_window
            visible: false // 初始状态为隐藏
            width: 400
            height: 300
            title: "工程属性"

            Loader {
                id: engineering_loader
                source: ""
                visible: source != ""
                active: engineering_loader.visible
                Layout.preferredWidth: 100
                Layout.fillHeight: true
            }
        }

        ApplicationWindow {
            id: video_window
            title:"视频同步"
            width: 170
            height: 220
            visible: false
            //color: "white"


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
