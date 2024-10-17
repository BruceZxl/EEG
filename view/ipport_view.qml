import QtQuick
import QtQuick.Controls
import WaveformPageViewModel


Item{
    property alias window: window
    property WaveformPageViewModel viewmodel: parent.viewmodel

    Window {
        id: window
        visible: true
        width: 400
        height: 300
        title: "网络通信"
        flags: Qt.Tool

        Column {

            Row {
                id: ipinput_row
                spacing: 10

                Text {
                    width: 90
                    height: 30
                    verticalAlignment: Text.AlignVCenter
                    renderType: Text.NativeRendering
                    text: "请输入IP地址："
                }

                ScrollView{
                    id: ipinput_view
                    width: 200
                    height: 60
                    background: Rectangle{
                        border.color: ipinput.activeFocus? "blue": "black"
                        border.width: ipinput.activeFocus? 2: 1
                    }
                    clip: true
                    ScrollBar.horizontal: ScrollBar{ visible:false }

                    //IP输入框
                    TextInput{
                        id: ipinput
                        width: ipinput_view.width
                        padding: 5
                        color: "black"
                        readOnly: false
                        //自定义光标样式
                        cursorDelegate: Rectangle{
                            width: 2
                            color: "blue"
                            property bool cursorRuning: ipinput.cursorVisible
                            visible: false
                            SequentialAnimation on visible {
                                id: cursorAnimation
                                running: false
                                loops: Animation.Infinite
                                PropertyAnimation { from:true; to: false; duration: 750 }
                                PropertyAnimation { from:false; to: true; duration: 500 }
                            }
                            onCursorRuningChanged: {
                                cursorAnimation.running=cursorRuning;
                                visible=cursorRuning;
                            }
                        }
                        selectByMouse: true
                        selectedTextColor: "white"
                        selectionColor: "black"
                        autoScroll: true
                        echoMode: TextInput.Normal
                        font{
                            family: "SimSun"
                            pixelSize: 16
                        }
                        renderType: Text.NativeRendering
                        wrapMode: TextInput.Wrap

                        //信号
                        onAccepted: {}
                        onEditingFinished: {}
                        onTextEdited: {}
                    }
                }
            }

            Row{
                id: portinput_row
                spacing: 10

                Text {
                    width: 90
                    height: 30
                    verticalAlignment: Text.AlignVCenter
                    renderType: Text.NativeRendering
                    text: "请输入端口号："
                }

                ScrollView{
                    id: portinput_view
                    width: 200
                    height: 60
                    background: Rectangle{
                        border.color: portinput.activeFocus? "blue": "black"
                        border.width: portinput.activeFocus? 2: 1
                    }
                    clip: true
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOn
                    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

                    //IP输入框
                    TextInput{
                        id: portinput
                        width: portinput_view.width
                        padding: 5
                        color: "black"
                        readOnly: false
                        //自定义光标样式
                        cursorDelegate: Rectangle{
                            width: 2
                            color: "blue"
                            property bool cursorRuning: portinput.cursorVisible
                            visible: false
                            SequentialAnimation on visible {
                                id: cursorAnimation1
                                running: false
                                loops: Animation.Infinite
                                PropertyAnimation { from:true; to: false; duration: 750 }
                                PropertyAnimation { from:false; to: true; duration: 500 }
                            }
                            onCursorRuningChanged: {
                                cursorAnimation1.running=cursorRuning;
                                visible=cursorRuning;
                            }
                        }
                        selectByMouse: true
                        selectedTextColor: "white"
                        selectionColor: "black"
                        autoScroll: true
                        echoMode: TextInput.Normal
                        font{
                            family: "SimSun"
                            pixelSize: 16
                        }
                        renderType: Text.NativeRendering
                        wrapMode: TextInput.Wrap

                        //信号
                        onAccepted: {}
                        onEditingFinished: {}
                        onTextEdited: {}
                    }
                }
            }

            Row {
                signal clicked()
                Button {
                    text: "确定"
                    onClicked: {
                        viewmodel.ip = ipinput.getText(0, 15)
                        viewmodel.port = portinput.getText(0, 5)
                        viewmodel.toggle_recv_mode()
                        viewmodel.auto_scroll = true
                        window.close()
                    }
                }
            }
        }
    }
}
