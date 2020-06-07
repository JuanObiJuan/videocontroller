import platform
import os
import sys
import time
import signal
import json
from PyQt5 import QtWidgets, QtGui, QtCore
import vlc
from gpiozero import LED

import json

import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO_SENSOR = 23
GPIO.setup(GPIO_SENSOR, GPIO.IN)

#The json format
  #"version": 202005111739,
  #"updateConfigUrl": "https://mydomain/config.json",
  #"mainVideo": "mainvideo.mp4",
  #"mainVideoUrl": "",
  #"introVideo": "introvideo.mp4",
  #"introVideoUrl": "",
  #"distance": 1500,
  #"loopMainVideoWhileUserInFront": true,
  #"mainVideoTimer": -1

localConfigFile = "/home/pi/Repository/videocontroller/config.json"

with open(localConfigFile) as json_file:
    localConfig = json.load(json_file)
    print("local config loaded")

minDistance = 10 # distance smaller than this will be ignored
startingDistance = localConfig["distance"]
loopMainVideo = localConfig["loopMainVideoWhileUserInFront"]
mainVideoTimerSec = localConfig["mainVideoTimer"]
introVideo = "/home/pi/introvideo.mp4"
mainVideo = "/home/pi/mainvideo.mp4"

breakMainVideo = (mainVideoTimerSec > -1)

pulseRelay = True
relayPulseTime = 0.3



#Now we have two channels to communicate with the lights
#This library is made for LEDS this means that led.on() is turning the gpio to 1 (3.3 Volts on)
#In our case Relais are active when the gpio is output is 0 led.off()
#To avoid to send both messages to the light system at the beggining
#We are going to use the output called "normally open" or "NO" and send a negative pulse to activate the signal
#In this way We avoid to send messages to the light system when the raspbery pi is booting or initialized
relay1=LED(22)
relay2=LED(27)
relay1.on()
relay2.on()

def distance():
    StartTime = time.time()
    StopTime = time.time()
    # save time of arrival
    while GPIO.input(GPIO_SENSOR) == 1:
        print("wait")
    while GPIO.input(GPIO_SENSOR) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_SENSOR) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed*10000*17)
    print(distance)
    return distance

def exit_handler(signal, frame):
    global running
    running = False
    GPIO.cleanup()
    QtWidgets.QApplication.quit()

# Attach a signal handler to catch SIGINT (Ctrl+C) and exit gracefully
signal.signal(signal.SIGINT, exit_handler)

class Player(QtWidgets.QMainWindow):

    def __init__(self, master=None):

        # setup qt window
        QtWidgets.QMainWindow.__init__(self, master)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BlankCursor)
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
        self.introVideo = self.instance.media_new(introVideo)
        self.mainVideo = self.instance.media_new(mainVideo)
        self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        self.waiting = True

        # set timer for callback
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.callback)
        self.timer.start()

    # def set_video(self, video):
    #     self.timer.stop()
    #     self.mediaplayer.set_media(video)
    #     self.mediaplayer.play()
    #     self.timer.start()

    # this is the set_video function to avoid the cutting of the beginning of the video
    # if there are problems with this use the function above

    def set_video(self, video):
        self.timer.stop()
        self.mediaplayer.set_media(video)
        self.mediaplayer.play()
        for i in range(15):
            time.sleep(0.02)
            self.mediaplayer.set_position(0.0)
        self.timer.start()

    def keyPressEvent(self,event):
        if(event.key() == QtCore.Qt.Key_Escape):
            tof.stop_ranging()
            self.close()

    # maybe this change in the future
    # and instead on/off we have to temporally
    # make a pulse (temporally on)
    def setInitialSceneStatus(self):
        #scene on on both casambi scenes
        relay1.off()
        relay2.off()
        time.sleep(relayPulseTime)
        relay1.on()
        relay2.on()
        #wait a reasonable time
        #and switch on scene 1
        time.sleep(relayPulseTime*8)
        relay1.off()
        time.sleep(relayPulseTime)
        relay1.on()
        self.waiting = True

    def setRelaisIntroVideo(self):
        #scene 1 on
        relay1.off()
        time.sleep(relayPulseTime)
        relay1.on()
        self.waiting = True

    def setRelaisMainVideo(self):
        #scene 1 off
        relay1.off()
        time.sleep(relayPulseTime)
        relay1.on()
        self.waiting = False


        #TODO: would be much more elegant with two different callback functions for the waiting states
    def callback(self):
        videoEnded = (self.mediaplayer.get_state() == 6)
        distance_in_mm = distance()
        userPresent = (distance_in_mm < startingDistance and distance_in_mm > minDistance)
        #TODO: this way a distance smaller than startingDistance is treated like no user is Present, this might not be a problem though.
        #      but it feels like it would be more logical if it's handled as the state of last call.
        #      or maybe test again??
        if(userPresent):
            self.lastTimeUserPresent = time.time()

        if(videoEnded):
            if(userPresent):
                self.set_video(self.mainVideo)
                if(self.waiting):
                    self.setRelaisMainVideo()
            else:
                self.set_video(self.introVideo)
                if(not self.waiting):
                    self.setRelaisIntroVideo()
            return

        if(self.waiting):
            if(userPresent):
                self.set_video(self.mainVideo)
                self.setRelaisMainVideo()
        elif(not userPresent and breakMainVideo):
            timeWithoutUser = time.time() - self.lastTimeUserPresent
            if(timeWithoutUser > mainVideoTimerSec):
                self.set_video(self.introVideo)
                self.setRelaisIntroVideo()

def main():
    app = QtWidgets.QApplication(sys.argv)
    player = Player()
    player.showFullScreen()
    player.relaisInitialization()
    player.set_video(player.introVideo)
    app.exec_()
    sys.exit(0)

if __name__ == "__main__":
    main()
