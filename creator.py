import json
import platform
import os
import ctypes

# Determine the directory of the current Python file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine the operating system
current_os = platform.system()

# Define the name of the shared library based on the operating system
if current_os == "Windows":
    lib_name = 'JsonMidiPlayer_ctypes.dll'
elif current_os == "Darwin":  # macOS
    lib_name = 'libJsonMidiPlayer_ctypes.dylib'
else:  # Assume Linux/Unix
    lib_name = 'libJsonMidiPlayer_ctypes.so'

# Construct the full path to the library
lib_path = os.path.join(script_dir, 'lib', lib_name)

# Check if the library file exists
if not os.path.isfile(lib_path):
    raise FileNotFoundError(f"COULD NOT FIND THE LIBRARY FILE: {lib_path}")
else:
    # Print the library path for debugging
    print(f"Library FOUND in: {lib_path}")
    try:
        # Load the shared library
        lib = ctypes.CDLL(lib_path)
        # Define the argument and return types for the C function
        lib.PlayList_ctypes.argtypes = [ctypes.c_char_p]
        lib.PlayList_ctypes.restype = ctypes.c_int

    except FileNotFoundError:
        print(f"Could not find the library file: {lib_path}")
    except OSError as e:
        print(f"An error occurred while loading the library: {e}")
    except AttributeError as e:
        print(f"An error occurred while accessing the function: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


class Configuration:
    ...



class PlayList:

    def __init__(self):
        ...


    def removeDevice(self, play_list, devicename):
        pass

    def printDevices(self, play_list):
        pass

    def setChannel(self, play_list, channel):
        pass

    def playPlayList(self, play_list):

        json_file_dict = {
                "filetype": "Json Midi Player",
                "content": play_list
            }
        # Convert Python dictionary to JSON string
        json_str = json.dumps([ json_file_dict ])

        try:
            # Call the C++ function with the JSON string
            lib.PlayList_ctypes(json_str.encode('utf-8'))
        except FileNotFoundError:
            print(f"Could not find the library file: {lib_path}")
        except OSError as e:
            print(f"An error occurred while loading the library: {e}")
        except AttributeError as e:
            print(f"An error occurred while accessing the function: {e}")
        except Exception as e:
            print(f"An unexpected error occurred when calling the function 'PlayList_ctypes': {e}")


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

