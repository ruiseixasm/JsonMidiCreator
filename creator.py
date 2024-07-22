import json
import platform
import os
import ctypes

class Configuration:
    ...



class PlayList:

    def __init__(self):
        # Determine the operating system
        self._current_os = platform.system()

        # Load the shared library based on the operating system
        if self._current_os == "Windows":
            self._lib_path = os.path.abspath('./libMidiJsonPlayer_ctypes.dll')
        elif self._current_os == "Darwin":  # macOS
            self._lib_path = os.path.abspath('./libMidiJsonPlayer_ctypes.dylib')
        else:  # Assume Linux/Unix
            self._lib_path = os.path.abspath('./libMidiJsonPlayer_ctypes.so')

        # Check if the library file exists
        if not os.path.isfile(self._lib_path):
            raise FileNotFoundError(f"Could not find the library file: {self._lib_path}")
            self._lib = None
        else:
            print(f"Found the library file: {self._lib_path}\n")
            # Load the shared library
            self._lib = ctypes.CDLL(self._lib_path)
            # Define the argument and return types for the C function
            self._lib.PlayList_ctypes.argtypes = [ctypes.c_char_p]

    def removeDevice(self, play_list, devicename):
        pass

    def printDevices(self, play_list):
        pass

    def setChannel(self, play_list, channel):
        pass

    def playPlayList(self, play_list):

        if self._lib is not None:
            json_file_dict = {
                    "filetype": "Midi Json Player",
                    "content": play_list
                }
            # Convert Python dictionary to JSON string
            json_str = json.dumps([ json_file_dict ])
            # Call the C++ function with the JSON string
            self._lib.PlayList_ctypes(json_str.encode('utf-8'))

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

