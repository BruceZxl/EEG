import QtQuick
import QtMultimedia
import QtQuick.Dialogs
import QtQuick.Controls
import QtQuick.Layouts
import WaveformPageViewModel

Item {
    id: root
    width: 300
    height: 300
    //property alias viewmodel: contentLoader.viewmodel

    FileDialog {
        id: fileDialog
        title: "Please choose a file"
        onAccepted: {
            videoPlayer.stop()
            videoPlayer.source = fileDialog.currentFile
            videoPlayer.play()
        }
    }

    MediaPlayer {
        id: videoPlayer
        videoOutput: videoOutput
    }

    Column {
        anchors.fill: parent

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

        VideoOutput {
            id: videoOutput
            width: 300
            height: 180
        }

        Row {
            width: 300
            Rectangle {
                id: start
                height: 20
                width: 20
                color: "grey"
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if (videoPlayer.playbackState === MediaPlayer.PausedState) {
                            videoPlayer.play()
                        } else if (videoPlayer.playbackState === MediaPlayer.PlayingState) {
                            videoPlayer.pause()
                        } else {
                            videoPlayer.play()
                        }
                    }
                }
            }
            Slider {
                id: mediaSlider
                width: 280
                enabled: videoPlayer.seekable
                from: 0
                to: 1.0
                value: videoPlayer.duration > 0 ? videoPlayer.position / videoPlayer.duration : 0

                onMoved: {
                    videoPlayer.setPosition(value * videoPlayer.duration)
                }
            }
        }
    }

    Connections {
        target: videoPlayer
        onMediaObjectChanged: {
            if (videoPlayer.mediaObject) {
                videoPlayer.mediaObject.notifyInterval = 50
            }
        }
    }
}