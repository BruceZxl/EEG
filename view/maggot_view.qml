import QtQuick
import WaveformView
import WaveformPageViewModel
import MaggotView
import WaveformAreaViewModel
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U

Item {
    property alias window: window
    property alias maggot_view: maggot_view
    id: root
    Window {
        id: window
        visible: true
        width: 400
        height: 300
        title: "放大镜"
        flags: Qt.Tool

        MaggotView {
            id: maggot_view
            anchors.centerIn: parent
            height: 300
            width: 400

            MouseArea {
                width: parent.width
                height: parent.height
                clip: true
                acceptedButtons: Qt.LeftButton | Qt.RightButton


                // 左键拖动触发移位，右键拖动触发
                onPressed: function(mouse) {
                    var ret_r = mouse.buttons & Qt.RightButton
                    var ret_l = mouse.buttons & Qt.LeftButton
                    if (ret_r) {
                        maggot_view.add_vertical_line(mouse.x)
                        maggot_view.select(mouse.x, mouse.y, false)
                    }
                    if (ret_l) {
                        maggot_view.drag_wave(mouse.x, false)
                    }
                }

                onPositionChanged: function(mouse) {
                    var ret_r = mouse.buttons & Qt.RightButton
                    var ret_l = mouse.buttons & Qt.LeftButton
                    if (ret_r) {
                        maggot_view.select(mouse.x, mouse.y, true)
                    }
                    if (ret_l) {
                        maggot_view.drag_wave(mouse.x, true)
                    }
                }

                onWheel:function(wheel)  {
                    maggot_view.zoom_wave(wheel.angleDelta.y)
                }
            }
        }
    }
}
