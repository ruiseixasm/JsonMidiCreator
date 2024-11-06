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

def saveJsonMidiPlay(play_list: list[dict], filename):
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
        
def jsonMidiPlay(play_list: list[dict], verbose: bool = False):
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

def saveMidiFile(midi_list: list[dict], filename="output.mid"):
    try:
        # pip install midiutil
        from midiutil import MIDIFile
    except ImportError:
        print("Error: The 'midiutil' library is not installed.")
        print("Please install it by running 'pip install midiutil'.")
        return

    processed_events: list[dict] = []
    # Starts by validating all events by time
    for event in midi_list:
        if all(key in event for key in ("event", "track", "track_name", "tempo", "time", "channel")):
            processed_events.append(event)
    processed_events = sorted(processed_events, key=lambda x: (x["track"], x["time"]))
    
    midi_tracks: set[int] = set()
    tracks_list: list[dict] = []
    for event in processed_events:
        if event["track"] not in midi_tracks:  # events already sorted (processed)
            midi_tracks.add(event["track"])    # sets don't allow duplicates nevertheless
            event_content: dict = {
                "track":        event["track"],
                "track_name":   event["track_name"],
                "tempo":        event["tempo"],
                "time":         event["time"]
            }
            tracks_list.append(event_content)
        event["time"] -= event_content["time"]  # Events are sorted by "track" and then by "time"

    MyMIDI = MIDIFile(len(midi_tracks))
    for track_content in tracks_list:
        MyMIDI.addTrackName(
            track_content["track"],
            track_content["time"],
            track_content["track_name"]
        )
        MyMIDI.addTempo(
            track_content["track"],
            track_content["time"],
            track_content["tempo"]
        )
    for event in processed_events:
        match event["event"]:
            case "Note":
                MyMIDI.addNote(
                    event["track"],
                    event["channel"],
                    event["pitch"],
                    event["time"],
                    event["duration"],
                    event["velocity"]
                )
            case "ControllerEvent":
                MyMIDI.addControllerEvent(
                    event["track"],
                    event["channel"],
                    event["time"],
                    event["number"],
                    event["value"]
                )
            case "PitchWheelEvent":
                MyMIDI.addPitchWheelEvent(
                    event["track"],
                    event["channel"],
                    event["time"],
                    event["value"]
                )
            case "ChannelPressure":
                MyMIDI.addChannelPressure(
                    event["track"],
                    event["channel"],
                    event["time"],
                    event["pressure"]
                )
            case "ProgramChange":
                MyMIDI.addProgramChange(
                    event["track"],
                    event["channel"],
                    event["time"],
                    event["program"]
                )
    with open(filename, "wb") as output_file:   # opened to write in binary mode
        MyMIDI.writeFile(output_file)

# Note Events
# addNote: Adds a note-on and note-off pair for a specific pitch, channel, time, duration, and velocity.
# Tempo and Time Events
# addTempo: Sets the tempo for a given track and time, in beats per minute (BPM).
# addTimeSignature: Adds a time signature event.
# addKeySignature: Adds a key signature event.
# Control Change (CC) Events
# addControllerEvent: Adds a MIDI Control Change (CC) message, which is often used for controls like modulation, volume, pan, etc. Each control number corresponds to a specific MIDI controller (e.g., control number 7 is volume).
# Program Change (PC) Events
# addProgramChange: Changes the instrument for a specified channel at a particular time, often used to switch between instrument sounds within a track.
# Pitch Bend and Aftertouch Events
# addPitchWheelEvent: Adds a pitch bend message for a specific channel.
# addChannelPressure: Adds a channel aftertouch (pressure) event for a specified channel and time.
# addPolyPressure: Adds polyphonic (per-note) aftertouch events for individual notes.
# System and Meta Events
# addSysEx: Adds a System Exclusive (SysEx) message to the track, useful for custom data specific to MIDI hardware or software.
# addUniversalSysEx: Adds a Universal System Exclusive message for broader, standard SysEx applications.
# addText: Adds text to the MIDI file, often for lyrics, titles, or other annotations.
# addCopyright: Adds copyright information to the file.
# addTrackName: Adds a name to the track, which appears in most MIDI editors.
# addMarker: Adds a marker at a specific point in the track, often for structural cues.
# addCuePoint: Adds a cue point for synchronizing MIDI with external media.

# #!/usr/bin/env python

# from midiutil import MIDIFile

# degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
# track    = 0
# channel  = 0
# time     = 0    # In beats
# duration = 1    # In beats
# tempo    = 60   # In BPM
# volume   = 100  # 0-127, as per the MIDI standard

# MyMIDI = MIDIFile(1)  # One track, defaults to format 1 (tempo track is created
#                       # automatically)
# MyMIDI.addTempo(track, time, tempo)

# for i, pitch in enumerate(degrees):
#     MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

# with open("major-scale.mid", "wb") as output_file:
#     MyMIDI.writeFile(output_file)

# https://pypi.org/project/MIDIUtil/

# In the line with open(filename, "wb") as output_file:, the "wb" stands for:

# w: This indicates that the file is being opened for writing. If the file already exists, it will be truncated (i.e., its contents will be erased). If the file does not exist, a new file will be created.
# b: This indicates that the file is being opened in binary mode. This is important when dealing with non-text files, such as MIDI files, which contain binary data.
# Alternatives
# Here are some common alternatives for the mode parameter in the open() function:

# "r": Open the file for reading (default mode). The file must exist.
# "rb": Open the file for reading in binary mode. Useful for reading binary files.
# "w": Open the file for writing. Creates a new file or truncates an existing file.
# "wb": Open the file for writing in binary mode.
# "a": Open the file for appending. Writes new data at the end of the file without truncating it.
# "ab": Open the file for appending in binary mode.
# "r+": Open the file for both reading and writing. The file must exist.
# "rb+": Open the file for both reading and writing in binary mode.
# These modes allow you to control how you interact with the file and whether you are reading from it, writing to it, or both.