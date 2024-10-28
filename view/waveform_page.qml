import QtQuick
import FrameSizes
import WaveformPageViewModel
import WaveformAreaViewModel
import QtQuick.Controls
import QtQuick.Layouts
// import QObject
import QtQuick.Controls.Universal as U




ColumnLayout {
    anchors.fill: parent

    property alias viewmodel: viewmodel
    property bool loadSine
    property bool neo
    property string path
    property string importFrom
    property string importFormat


    //FPS
    function tess(times) {
        var sum = 0.0;
        for (let i = 0; i < areas.count; i++) sum += areas.itemAt(i).item.tess(times)
        let fps = Math.round(times / sum);
        console.log(`FPS: ${fps}`)
        return fps
    }


    WaveformPageViewModel {
        id: viewmodel
        Component.onCompleted: reload(path, neo, loadSine, importFrom, importFormat)
        Component.onDestruction: unload()
    }


    //画布
    Repeater {
        id: areas
        model: viewmodel.area_viewmodels
        delegate: Loader {
            source: "waveform_area.qml"
            active: true
            readonly property WaveformPageViewModel page_viewmodel: viewmodel
            readonly property WaveformAreaViewModel area_viewmodel: modelData
            // Layout.preferredHeight: 1
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
    }

    //滚动条
    ScrollBar {
        Layout.fillWidth: true
        height: 10
        policy: ScrollBar.AlwaysOn
        orientation: Qt.Horizontal
        hoverEnabled: true
        active: true
        minimumSize: 0.1
        size: width / (viewmodel?.area_viewmodels[0]?.scale ?? 1) / viewmodel.seconds
        position: viewmodel.position / viewmodel.seconds
        onPositionChanged: {
            if (pressed) viewmodel.seek(position * viewmodel.seconds);
        }
    }
}
