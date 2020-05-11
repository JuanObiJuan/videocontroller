import platform
import os
import sys
import signal
from PyQt5 import QtWidgets, QtGui, QtCore
import vlc
from gpiozero import LED
import VL53L1X

startingDistance = 1500
introVideo = "/home/pi/videointro.mp4"
mainVideo = "/home/pi/t.mp4"

# Open and start the VL53L1X sensor.
tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
tof.open()
tof.start_ranging(3)  # Start ranging
                      # 0 = Unchanged
                      # 1 = Short Range
                      # 2 = Medium Range
                      # 3 = Long Range

#Now we have two channels to communicate with the lights
relay1=LED(27)
relay2=LED(17)

def exit_handler(signal, frame):
    global running
    running = False
    tof.stop_ranging()
    QtWidgets.QApplication.quit()

# Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
signal.signal(signal.SIGINT, exit_handler)

class Player(QtWidgets.QMainWindow):

    def __init__(self, master=None):

        # setup qt window
        QtWidgets.QMainWindow.__init__(self, master)
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)
        self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.setContentsMargins(0,0,0,0)
        self.vboxlayout.addWidget(self.videoframe)
        self.widget.setLayout(self.vboxlayout)

        # create vlc instance + load videos
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.waitVideo = self.instance.media_new(introVideo)
        self.video = self.instance.media_new(mainVideo)
        self.waiting = True

        # set timer for callback
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.callback)
        self.timer.start()

    def set_video(self, video):
        self.timer.stop()
        self.mediaplayer.set_media(video)
        self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        self.mediaplayer.play()
        self.timer.start()

    # maybe this change in the future
    # and instead on/off we have to temporally
    # make a pulse (temporally on)

    def setRelaisIntroVideo(self):
        relay1.on()
        relay2.off()

    def setRelaisMainVideo(self):
        relay2.on()
        relay1.off()

    def callback(self):
        self.timer.stop()

        # if the video has ended start the intro-video.
        if(self.mediaplayer.get_state() == 6):
            if(not self.waiting):
                # set relais for light situation for the intro video
                self.setRelaisIntroVideo()
            self.set_video(self.waitVideo)
            self.waiting = True

        # start video if distance is lower than startingDistance
        if(self.waiting):
            distance_in_mm = tof.get_distance()
            if (distance_in_mm < startingDistance and distance_in_mm > -1):
                # set relais for light situation for the Main video
                self.setRelaisMainVideo()
                self.set_video(self.video)
                self.waiting = False

        self.timer.start()

def main():
    app = QtWidgets.QApplication(sys.argv)
    player = Player()
    player.showFullScreen()
    player.set_video(player.waitVideo)
    #player.show()
    #player.resize(800,600)
    app.exec_()
    tof.stop_ranging()
    sys.exit(0)

if __name__ == "__main__":
    main()

