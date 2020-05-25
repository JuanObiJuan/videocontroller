import json
import urllib.request
import os
import time

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

# just wait for "timeToWaitForWifi" Seconds
timeToWaitForWifi = 10
time.sleep(timeToWaitForWifi)

# wifiConnected = False
# os.system('notify-send "wifi" "waiting for wifi to connect"')
# for i in range(0, timeToWaitForWifi):
#     wifistatus = open("/sys/class/net/wlan0/operstate")
#     if(wifistatus.read() == "up\n"):
#         wifiConnected = True
#         break
#     time.sleep(1)

if(wifiConnected):
    os.system('notify-send "wifi" "wifi connected"')
else:
    os.system('notify-send "wifi" "no wifi connection"')


# if the url can't be opened set "remoteConfig = localConfig"
try:
    json_url_content= urllib.request.urlopen(localConfig["updateConfigUrl"])
    remoteConfig = json.load(json_url_content)
    print("remote config loaded")
except:
    remoteConfig = localConfig
    print("No access to remote config")
    os.system('notify-send "no access" "the device has no acces to check new updates"')

if(remoteConfig["version"]>localConfig["version"]):
  #download new videos
  print("new videos!")
  os.system('notify-send "updating" "...downloading new videos"')
  try:
    urllib.request.urlretrieve(remoteConfig["introVideoUrl"],r"/home/pi/introvideo_new.mp4")
    urllib.request.urlretrieve(remoteConfig["mainVideoUrl"],r"/home/pi/mainvideo_new.mp4")
  except:
    print("could not download new video files")
    os.system('notify-send "error" "Something went wrong updating the videos"')
  else:
    print("video update complete")
    os.system('notify-send "ok" "Update was successfull"')
    # overwrite old videos
    os.rename("/home/pi/introvideo_new.mp4","/home/pi/introvideo.mp4")
    os.rename("/home/pi/mainvideo_new.mp4","/home/pi/mainvideo.mp4")
    #update the local config file
    json.dump(remoteConfig ,open(localConfigFile,"w"),indent=2)

os.system('notify-send "loading" "Loading player"')
os.system('python3 /home/pi/Repository/videocontroller/mus.py')
