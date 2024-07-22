import json
import platform
import os
import ctypes

# Determine the operating system
current_os = platform.system()

# Load the shared library based on the operating system
if current_os == "Windows":
    lib_path = os.path.abspath('./libMidiJsonPlayer_lib.dll')
else:  # Assume Linux/Unix
    lib_path = os.path.abspath('./libMidiJsonPlayer_lib.so')

# Check if the library file exists
if not os.path.isfile(lib_path):
    raise FileNotFoundError(f"Could not find the library file: {lib_path}")
else:
    print(f"Found the library file: {lib_path}")

# # Load the shared library
# lib = ctypes.CDLL(lib_path)

# # Define the argument and return types for the C function
# lib.PlayList.argtypes = [ctypes.c_char_p]

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
        # Convert Python dictionary to JSON string
        json_str = json.dumps(play_list)

        # Call the C++ function with the JSON string
        lib.PlayList(json_str.encode('utf-8'))


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

