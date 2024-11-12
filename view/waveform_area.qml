import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Universal as U
import WaveformView
import FrameSizes
import TimeDeltaViewModel
import WaveformPageViewModel
import WaveformAreaViewModel
ColumnLayout {
    id: root
    readonly property WaveformPageViewModel page_viewmodel: parent.page_viewmodel
    readonly property WaveformAreaViewModel viewmodel: parent.area_viewmodel
    readonly property int channeLabelWidth: 100
    Component.onCompleted:{
            timer.start()
       }

    function tess(times) {
        return waveform.tess(times)
    }

    Row {
        padding: 10  //周围填充
        spacing: 10  //距离

        Label {  //标签 帧大小
            text: "帧大小" //帧大小标签
        }

        //ComboBox是一个组合按钮和弹出列表
        ComboBox { //旁边的下拉菜单  帧大小时间调节
            textRole: "text"
            valueRole: "value"
            model: FrameSizes.get_all()  //为组合框提供数据的模型  才能够出现 1s  2S  30S
            currentIndex: waveform.frame_size //组合框中当前项目的索引  即初次运行时 显示的列表中的选项
            onActivated: function (index) {
                waveform.frame_size = index;
            }
        }

        // Label {  //标签 帧大小
        //     text: "呼吸事件标注" //帧大小标签
        // }
        //
        // Button {
        //     text: "中枢型呼吸事件"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:function(mouse){
        //            contentLoader.item.viewmodel.mark_breathe_event_num = 0;
        //
        //     }
        //     background: Rectangle {
        //         color: "red"
        //         opacity: 0.6
        //     }
        // }
        // Button {
        //     text: "阻塞型呼吸事件"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.mark_breathe_event_num = 1;
        //     }
        //     background: Rectangle {
        //         color: "green"
        //         opacity: 0.6
        //     }
        // }
        // Button {
        //     text: "混合型呼吸事件"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.mark_breathe_event_num = 2;
        //     }
        //     background: Rectangle {
        //         color: "blue"
        //         opacity: 0.6
        //     }
        // }
        //
        // Button {
        //     text: "自动标注"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.auto_breathe_event_annotate_flag = 1
        //     }
        // }
        //
        // Button {
        //     text: "确定/保存"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.set_save_flag = 1
        //     }
        // }
        //
        // Button {
        //     text: "删除"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.set_delete_flag = 1
        //     }
        // }
        //
        // Button {
        //     text: "保存到数据库"
        //     Layout.fillWidth: true
        //     Layout.preferredWidth: 30
        //     onClicked:{
        //         contentLoader.item.viewmodel.save_mark_breathe_event_record = 1
        //     }
        // }
    }



    Flickable {
        
        id: main_scroller
        Layout.fillWidth: true
        Layout.fillHeight: true
        contentHeight: waveform.height
        contentWidth: width
        clip: true
        ScrollBar.vertical: U.ScrollBar {}

        RowLayout {
            width: main_scroller.contentWidth


            //通道标签
            Column {
                Repeater {
                    model: viewmodel.montage_block_viewmodel.channels
                    delegate: Text {
                        text: modelData.name
                        width: channeLabelWidth
                        height: contentLoader.height / (area_viewmodel.montage_block_viewmodel.num_channels + 1)
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                }
            }

            WaveformView {
                id: waveform
                Layout.fillWidth: true
                Layout.alignment: Qt.AlignTop
                height: 100
                property alias page_viewmodel: root.page_viewmodel
                property alias viewmodel: root.viewmodel
                Timer{
                    id:timer02
                    repeat: true
                    interval: 16
                    onTriggered:{
                        waveform.scroll(waveform.frame_size)
                    }
                }


                Timer {
                    id: timer
                    repeat: true
                    interval: 16
                    property var scrollState: [0, false]

                    onTriggered: {
                        // there's no scrolling physics from QT
                        // no need for a industrial standard scroll controller
                        // just monkey-engineer it like this :(
                        const friction = 10.0
                        const mass = 300.0
                        let delta = page_viewmodel.render_time + interval
                        let stoppedCount = 0;
                        waveform.auto_scroll()
                        for (let stateAndFunc of [
                            [scrollState, waveform.scroll]
                        ]) {
                            let state = stateAndFunc[0]
                            let func = stateAndFunc[1]
                            if (state[0] <= 0) {
                                stoppedCount += 1
                                continue
                            }
                            let movement = state[0] * delta / mass
                            if (!state[1]) movement = -movement
                            func(movement)
                            state[0] -= (friction * delta)
                            if (state[0] <= 0) {
                                state[0] = 0
                                stoppedCount += 1
                            }
                        }
                        interval = Math.max(1, (16 - page_viewmodel.render_time))
                        //if (stoppedCount >= 1 && page_viewmodel._project == null) stop()
                    }
                }

                MouseArea {
                    width: parent.width
                    height: parent.height
                    clip: true
                    preventStealing: page_viewmodel.maggot_mode

                    onPressed: function(mouse) {
                        if (page_viewmodel.maggot_mode)
                        {
                            viewmodel.set_selection_point(mouse.x, mouse.y, false);
                            maggot_window.item.maggot_view.wave_index=waveform.get_index
                         }
                        if (page_viewmodel.position_mode)
                        {
                            page_viewmodel.update_position_y(mouse.y)
                        }

                    }
                    onPositionChanged: function(mouse) {
                        if (page_viewmodel.maggot_mode)
                        {
                            viewmodel.set_selection_point(mouse.x, mouse.y, true);
                            maggot_window.item.maggot_view.wave_index=waveform.get_index

                        }
                        if (page_viewmodel.position_mode)
                        {
                            page_viewmodel.update_position_y(mouse.y)
                        }

                    }

                    onWheel: function(wheel) {
                        // touchpad, like Mac's
                        if (wheel.pixelDelta.x != 0 || wheel.pixelDelta.y != 0) {
                            if (wheel.pixelDelta.x != 0) waveform.scroll(wheel.pixelDelta.x)
                            wheel.pixelDelta.x = 0
                            wheel.accepted = false
                            return
                        }
                        // for those having horizontal wheels
                        if (wheel.angleDelta.x != 0) {
                            fluentScrollOrZoom(wheel.angleDelta.x, [wheel.angleDelta.x], timer.scrollState)
                            wheel.angleDelta.x = 0
                            wheel.accepted = false
                            return
                        }
                        // ctrl + wheel => zoom
                        if (wheel.modifiers & Qt.ControlModifier) {
                            waveform.zoom(wheel.y, -wheel.angleDelta.y)
                            return
                        }
                        // shift + vertical whell => vertical scroll => pass to parent scroll view
                        if (wheel.modifiers & Qt.ShiftModifier) {
                            wheel.accepted = false
                            return
                        }
                        // ordinary wheel
                        if (wheel.angleDelta.y != 0) {
                            fluentScrollOrZoom(-wheel.angleDelta.y, [-wheel.angleDelta.y], timer.scrollState)
                        }
                    }

                    function fluentScrollOrZoom(amount, args, state) {
                        timer.start()
                        let velocityDirection = amount > 0
                        if (state[1] != velocityDirection) state[0] = 0
                        state[0] = Math.max(state[0] + Math.abs(amount), 1000)
                        state[1] = velocityDirection
                    }
                }
            }
        }
    }


    Loader{
        id: maggot_window
        active:page_viewmodel.maggot_mode??true
        source:"maggot_view.qml"
        }

    Connections{
        target: maggot_window.item?.window ?? null
            function onClosing(val) {
            page_viewmodel.maggot_mode = false
            }
        }
    RowLayout {
        Layout.fillWidth: true

        Rectangle {
            width: channeLabelWidth
        }

        Item {
            Layout.fillWidth: true
            height: 20
            readonly property real spacing: 20
            readonly property int majorEvery: 10
            property real pixelPosition: page_viewmodel.position * (viewmodel?.scale ?? 1.)
            property real rawOffset: pixelPosition % spacing
            property real offset: rawOffset > 0 ? spacing - rawOffset: rawOffset
            property int majorOffset: Math.ceil(pixelPosition / spacing) % majorEvery

            TimeDeltaViewModel {
                id: timedelta_viewmodel_axis
            }

            TimeDeltaViewModel {
                id: timedelta_viewmodel_axis_ref
            }

            Repeater {
                model: Math.max(parent.width / parent.spacing - 1, 0)
                delegate: Rectangle {
                    x: index * parent.spacing + parent.offset
                    implicitWidth: major ? 2  : 1
                    implicitHeight: parent.height * .4 * (major ? 2 : 1)
                    color: "grey"
                    readonly property bool major: (index + parent.majorOffset) % parent.majorEvery == 0
                }
            }

            Repeater {
                model: Math.max((parent.width / parent.spacing - 1) / parent.majorEvery, 0)
                delegate: Text {
                    readonly property real baseX: (index * parent.majorEvery + (parent.majorOffset > 0 ? parent.majorEvery - parent.majorOffset : parent.majorOffset)) * parent.spacing + parent.offset
                    x: baseX + parent.spacing
                    text: formatTime()
                    color: "grey"

                    function formatTime() {
                        let t = page_viewmodel.position + baseX / (viewmodel?.scale ?? 1.)
                        timedelta_viewmodel_axis.total_ms = t * 1000
                        timedelta_viewmodel_axis.normalize()
                        let cm = parent.majorEvery * parent.spacing / (viewmodel?.scale ?? 1.)
                        if (cm > 2) cm = 1100
                        else if (cm > 1) cm = 1010
                        else if (cm > .2) cm = 104                        
                        else cm = 1
                        timedelta_viewmodel_axis_ref.total_ms = cm
                        timedelta_viewmodel_axis_ref.normalize()
                        return timedelta_viewmodel_axis.to_readable(timedelta_viewmodel_axis_ref, true)
                    }
                }
            }
        }

    }

    Connections {
        target: viewmodel
        function onCanvasInvalidated() {
            waveform.update()
        }
    }
}
