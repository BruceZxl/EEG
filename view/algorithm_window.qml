import Qt.labs.platform 1.1
import OSColors
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import AlgorithmViewModel

ApplicationWindow {
    visible: true
    width: 800
    height: 600
    title: "算法选择和参数配置"
    color: "white"

    property string modelFilePath: ""
    property string dataFilePath: ""
    property var numberList: []
    property int labelCount: 3

    Rectangle {
        anchors.fill: parent
        color: "white"

        ColumnLayout {
            anchors.fill: parent
            spacing: 10


            MenuBar {
                Menu {
                    title: qsTr("&文件")
                    Action {
                        text: qsTr("&退出")
                        onTriggered: Qt.quit()
                    }
                }
            }

            GroupBox {
                title: "文件操作"
                Layout.fillWidth: true
                RowLayout {
                    spacing: 10
                    Button {
                        text: "加载模型"
                        onClicked: modelFileDialog.visible = true
                    }
                    Button {
                        text: "加载数据"
                        onClicked: dataFileDialog.visible = true
                    }
                }
            }

            GroupBox {
                title: "算法配置"
                Layout.fillWidth: true
                ColumnLayout {
                    spacing: 10
                    CheckBox {
                        id: algorithmCheckBox
                        text: "启用算法"
                        checked: false
                        onCheckedChanged: parametersColumn.visible = checked
                    }

                    ColumnLayout {
                        id: parametersColumn
                        visible: false
                        spacing: 10

                        RowLayout {
                            spacing: 10
                            Label {
                                text: "标签数量:"
                            }
                            SpinBox {
                                id: spinBoxLabelCount
                                from: 1
                                to: 10
                                value: 3
                                onValueChanged: labelCount = value
                            }
                        }

                        RowLayout {
                            spacing: 10
                            Label {
                                text: "算法参数:"
                            }
                            TextField {
                                placeholderText: "输入算法参数"
                            }
                        }

                        RowLayout {
                            spacing: 10
                            Label {
                                text: "数据处理选项:"
                            }
                            ComboBox {
                                model: ["选项1", "选项2", "选项3"]
                            }
                        }
                    }
                }
            }

            GroupBox {
                title: "操作"
                Layout.fillWidth: true
                ColumnLayout {
                    spacing: 10
                    Button {
                        text: "获取预测结果"
                        onClicked: AlgorithmViewModel.predict(modelFilePath, dataFilePath)
                    }

                    ListView {
                        id: predictionListView
                        Layout.fillWidth: true
                        height: 200
                        model: numberList
                        delegate: Item {
                            width: parent.width
                            height: 30
                            Text {
                                text: modelData
                                anchors.centerIn: parent
                            }
                        }
                    }
                }
            }
        }
    }

    FileDialog {
        id: modelFileDialog
        title: "选择模型文件"
        folder: shortcuts.home
        onAccepted: {
            modelFilePath = file
            console.log("模型文件路径: " + modelFilePath)
        }
        onRejected: {
            console.log("模型文件选择被取消")
        }
    }

    FileDialog {
        id: dataFileDialog
        title: "选择数据文件"
        folder: shortcuts.home
        onAccepted: {
            dataFilePath = file
            console.log("数据文件路径: " + dataFilePath)
        }
        onRejected: {
            console.log("数据文件选择被取消")
        }
    }

    Connections {
        target: AlgorithmViewModel
        onPredictionChanged: numberList = arguments[0]
    }
}
