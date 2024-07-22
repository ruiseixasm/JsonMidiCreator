import json

class Configuration:
    ...

class PlayList:

    def __init__(self):
        pass

    def removeDevice(play_list, devicename):
        pass

    def printDevices(play_list):
        pass

    def setChannel(play_list, channel):
        pass

    def saveJson(self, json_list, filename):
        pass

    def loadJson(self, filename):
        pass

    def saveJsonPlay(self, play_list, filename):
        json_file_dict = {
                "filetype": "Midi Json Player",
                "content": play_list
            }
        
        with open(filename, "w") as outfile:
            json.dump(json_file_dict, outfile)

