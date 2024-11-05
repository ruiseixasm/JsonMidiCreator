'''
JsonMidiCreator - Json Midi Creator is intended to be used
in conjugation with the Json Midi Player to Play composed Elements
Original Copyright (c) 2024 Rui Seixas Monteiro. All right reserved.
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Lesser General Public License for more details.
https://github.com/ruiseixasm/JsonMidiCreator
https://github.com/ruiseixasm/JsonMidiPlayer
'''
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
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/Windows/lib/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'JsonMidiPlayer_ctypes.dll' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
elif current_os == "Darwin":  # macOS
    lib_name = 'libJsonMidiPlayer_ctypes.dylib'
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/MacOS/lib/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'libJsonMidiPlayer_ctypes.dylib' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
else:  # Assume Linux/Unix
    lib_name = 'libJsonMidiPlayer_ctypes.so'
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/Linux/lib/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'libJsonMidiPlayer_ctypes.so' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"

# Construct the full path to the library
lib_path = os.path.join(script_dir, '..', 'lib', lib_name)

available_library = os.path.isfile(lib_path)
lib = None
not_found_library_message_already_shown = False

# Check if the library file exists
def loadLibrary():
    global available_library
    global lib
    global not_found_library_message_already_shown
    if available_library:
        if not lib:
            # Print the library path for debugging
            # print(f"Library FOUND in: {lib_path}")
            try:
                # Load the shared library
                lib = ctypes.CDLL(lib_path)
                # Define the argument and return types for the C function
                lib.PlayList_ctypes.argtypes = [ctypes.c_char_p, ctypes.c_int]
                lib.PlayList_ctypes.restype = ctypes.c_int
                
            except FileNotFoundError:
                print(f"Could not find the library file: {lib_path}")
                available_library = False
            except OSError as e:
                print(f"An error occurred while loading the library: {e}")
                available_library = False
            except AttributeError as e:
                print(f"An error occurred while accessing the function: {e}")
                available_library = False
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                available_library = False
    elif not not_found_library_message_already_shown:
        print(not_found_library_message)
        not_found_library_message_already_shown = True

def saveJsonMidiCreator(serialization: dict, filename):
    json_file_dict = {
            "filetype": "Json Midi Creator",
            "url": "https://github.com/ruiseixasm/JsonMidiCreator",
            "content": serialization
        }
    with open(filename, "w") as outfile:
        json.dump(json_file_dict, outfile)

def loadJsonMidiCreator(filename):
    try:
        with open(filename, "r") as infile:
            json_file_dict = json.load(infile)
        if "content" in json_file_dict and "filetype" in json_file_dict and \
                json_file_dict["filetype"] == "Json Midi Creator" and json_file_dict["url"] == "https://github.com/ruiseixasm/JsonMidiCreator":
            return json_file_dict["content"]
    except Exception as e:
        print(f"Unable to Load the file: {filename}")
    return []

def saveJsonMidiPlay(play_list, filename):
    json_file_dict = {
            "filetype": "Json Midi Player",
            "url": "https://github.com/ruiseixasm/JsonMidiPlayer",
            "content": play_list
        }
    with open(filename, "w") as outfile:
        json.dump(json_file_dict, outfile)
        
def loadJsonMidiPlay(filename):
    try:
        with open(filename, "r") as infile:
            json_file_dict = json.load(infile)
        if "content" in json_file_dict and "filetype" in json_file_dict and \
                json_file_dict["filetype"] == "Json Midi Player" and json_file_dict["url"] == "https://github.com/ruiseixasm/JsonMidiPlayer":
            return json_file_dict["content"]
    except Exception as e:
        print(f"Unable to Import the file: {filename}")
    return []
        
def jsonMidiPlay(play_list, verbose: bool = False):
    global lib
    global not_found_library_message_already_shown
    if not lib and not not_found_library_message_already_shown: loadLibrary()
    if lib:
        if verbose: print() # Avoids verbose cluttering
        json_file_dict = {
                "filetype": "Json Midi Player",
                "url": "https://github.com/ruiseixasm/JsonMidiPlayer",
                "content": play_list
            }
        # Convert Python dictionary to JSON string
        json_str = json.dumps([ json_file_dict ])

        try:
            # Call the C++ function with the JSON string
            lib.PlayList_ctypes(json_str.encode('utf-8'), 1 if verbose else 0)
        except FileNotFoundError:
            print(f"Could not find the library file: {lib_path}")
        except OSError as e:
            print(f"An error occurred while loading the library: {e}")
        except AttributeError as e:
            print(f"An error occurred while accessing the function: {e}")
        except Exception as e:
            print(f"An unexpected error occurred when calling the function 'PlayList_ctypes': {e}")

def create_midi_file(filename="output.mid"):
    try:
        # pip install midiutil
        from midiutil import MIDIFile
    except ImportError:
        print("Error: The 'midiutil' library is not installed.")
        print("Please install it by running 'pip install midiutil'.")
        return
    
    
