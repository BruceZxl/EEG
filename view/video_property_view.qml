import QtQuick
import QtMultimedia
import QtQuick.Dialogs
import QtQuick.Controls
import QtQuick.Layouts
import WaveformPageViewModel

Window {
    id: root
    title:"视频同步"
    width: 170
    height: 220
    visible: true
    color: "white"
    property WaveformPageViewModel viewmodel:parent.viewmodel
        FileDialog {
        id: fileDialog
        title: "Please choose a file"
        onAccepted: {
            videoPlayer.stop()
            videoPlayer.source = fileDialog.currentFile
            videoPlayer.play()
        }
    }
    Component.onCompleted: {
        x = 315  // 固定的水平位置
        y = 670  // 固定的垂直位置
    }
    //播放显示视频
    MediaPlayer {
        id: videoPlayer
        //指定视频的地址

        //音量范围从0到1
        videoOutput: videoOutput
    }
    Row{
        //视频输出窗口
        Column{
    MenuBar {
        id: menuBar


        Menu {
            title: qsTr("&File")
            Action {
                text: qsTr("&Open")
                onTriggered: fileDialog.open()
            }
        }
    }
            VideoOutput{
                id:videoOutput
                width: 300
                height: 180

            }
            Row{
                width:300
            Rectangle{
                id:start
                height:20
                width:20
                color: "grey"
                MouseArea{
                    anchors.fill:parent
                onClicked: {
                if (videoPlayer.playbackState === 2) {
                    videoPlayer.play()
                } else if (videoPlayer.playbackState === 1) {
                    videoPlayer.pause()
                } else {
                    videoPlayer.play()
                }
            }
                }
            }
        Slider {
            id: mediaSlider
            width:280
            enabled: videoPlayer.seekable
            to: 1.0
            value: videoPlayer.position / videoPlayer.duration

            onMoved:
            {
                videoPlayer.setPosition(value *videoPlayer.duration);
             }
        }
        }}
    }
    //通过修改更新的时间间隔,提升视频交互的平滑性
    Connections {
            target: videoPlayer
            onMediaObjectChanged: {
                if (videoPlayer.mediaObject) {
                    videoPlayer.mediaObject.notifyInterval = 50;
                }
            }
        }


}