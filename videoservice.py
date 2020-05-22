import json
import urllib.request
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


localConfigFile = "/home/pi/config.json"


with open(localConfigFile) as json_file:
    localConfig = json.load(json_file)

# if the url can't be opened set "remoteConfig = localConfig"
try:
    json_url_content= urllib.request.urlopen(localConfig["updateConfigUrl"])
    remoteConfig = json.load(json_url_content)
except:
    remoteConfig = localConfig

if(remoteConfig["version"]>localConfig["version"]):
  #download new videos
  try:
    urllib.request.urlretrieve(remoteConfig["introVideoUrl"],r"/home/pi/introvideo_new.mp4")
    urllib.request.urlretrieve(remoteConfig["mainVideoUrl"],r"/home/pi/mainvideo_new.mp4")
  except:
    print("could not download new video files")
  else:
    print("video update complete")
    # overwrite old videos
    os.rename("/home/pi/introvideo_new.mp4","/home/pi/introvideo.mp4")
    os.rename("/home/pi/mainvideo_new.mp4","/home/pi/mainvideo.mp4")
    #update the local config file
    json.dump(remoteConfig ,open(localConfigFile,"w"),indent=2)

import mus
mus.main()
