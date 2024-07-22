import json
import ctypes

class Configuration:
    ...

class PlayList:

    def __init__(self):
        pass

    def removeDevice(self, play_list, devicename):
        pass

    def printDevices(self, play_list):
        pass

    def setChannel(self, play_list, channel):
        pass

    def playPlayList(self, play_list):
        ...

    def saveJson(self, json_list, filename):
        pass

    def loadJson(self, filename):
        pass

    def saveJsonPlayList(self, play_list, filename):
        json_file_dict = {
                "filetype": "Midi Json Player",
                "content": play_list
            }
        
        with open(filename, "w") as outfile:
            json.dump(json_file_dict, outfile)

