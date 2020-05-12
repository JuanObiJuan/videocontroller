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



with open('/home/pi/config.json') as json_file:
    localConfig = json.load(json_file)

#TODO take care of no internet connection
json_url_content= urllib.request.urlopen(localConfig["updateConfigUrl"])
remoteConfig = json.load(json_url_content)

if(remoteConfig["version"]>localConfig["version"]):
  print("update videos and run mus.py")
  #download new videos
  #delete the old ones
  #update the local config file
  #run mus.py
else:
  #run mus.py
