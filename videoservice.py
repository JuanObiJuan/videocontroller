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

#TODO take care of no internet connection
json_url_content= urllib.request.urlopen(localConfig["updateConfigUrl"])
remoteConfig = json.load(json_url_content)

if(remoteConfig["version"]>localConfig["version"]):
  print("update videos and run mus.py")
  #download new videos and overwrite old ones
  urllib.request.urlretrieve(remoteConfig["introVideoUrl"],r"/home/pi/introvideo.mp4")
  urllib.request.urlretrieve(remoteConfig["mainVideoUrl"],r"/home/pi/mainvideo.mp4")
  #update the local config file
  json.dump(remoteConfig ,open(localConfigFile,"w"),indent=2)

#run mus.py
