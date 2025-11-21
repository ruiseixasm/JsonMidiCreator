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
import threading
# import multiprocessing
import math
import time

# Determine the directory of the current Python file
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine the operating system
current_os = platform.system()

# Define the name of the shared library based on the operating system
if current_os == "Windows":
    lib_name = 'JsonMidiPlayer_ctypes.dll'
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/Windows/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'JsonMidiPlayer_ctypes.dll' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
    talkie_lib = 'JsonTalkiePlayer_ctypes.dll'
elif current_os == "Darwin":  # macOS
    lib_name = 'libJsonMidiPlayer_ctypes.dylib'
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/MacOS/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'libJsonMidiPlayer_ctypes.dylib' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
    talkie_lib = 'libJsonTalkiePlayer_ctypes.dylib'
else:  # Assume Linux/Unix
    lib_name = 'libJsonMidiPlayer_ctypes.so'
    not_found_library_message = \
        f">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n" + \
        f"Library NOT found, please go to 'https://sourceforge.net/projects/json-midi-player/files/Linux/' for the compiled Library\n" + \
        f"or go to 'https://github.com/ruiseixasm/JsonMidiPlayer' for the source files to compile the 'libJsonMidiPlayer_ctypes.so' file\n" + \
        f"and place it inside the local folder 'lib'.\n" + \
        f"<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
    talkie_lib = 'libJsonTalkiePlayer_ctypes.so'


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


# Construct the full path to the library
talkie_lib_path = os.path.join(script_dir, '..', 'lib', talkie_lib)
available_talkie_library = os.path.isfile(talkie_lib_path)
talkie_lib = None
not_found_talkie_library = False

# Check if the library file exists
def loadTalkieLibrary():
    global available_talkie_library
    global talkie_lib
    global not_found_talkie_library
    if available_talkie_library:
        if not talkie_lib:
            try:
                # Load the shared library
                talkie_lib = ctypes.CDLL(talkie_lib_path)
                # Define the argument and return types for the C function
                talkie_lib.PlayList_ctypes.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
                talkie_lib.PlayList_ctypes.restype = ctypes.c_int
                
            except Exception as e:
                available_talkie_library = False
                not_found_talkie_library = True


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


# Function to run the DLL in a separate thread
def run_dll(json_str, verbose):
    if lib:
        try:
            # Call the C++ function with the JSON string
            lib.PlayList_ctypes(json_str.encode('utf-8'), 1 if verbose else 0)
        except Exception as e:
            print(f"An error occurred when calling the function 'PlayList_ctypes': {e}")

# Function to run the DLL in a separate thread
def run_talkie_dll(json_str, delay_ms, verbose):
    if talkie_lib:
        try:
            # Call the C++ function with the JSON string
            talkie_lib.PlayList_ctypes(json_str.encode('utf-8'), delay_ms, 1 if verbose else 0)
        except Exception as e:
            print(f"An error occurred when calling the function 'PlayList_ctypes': {e} for JsonTalkiePlayer")

def jsonMidiPlay(play_list: list[dict], verbose: bool = False, talkie_delay_ms: int = 500):
    global lib
    global not_found_library_message_already_shown
    if not lib and not not_found_library_message_already_shown: loadLibrary()
    if not talkie_lib and not not_found_talkie_library: loadTalkieLibrary()
    if lib:
        if verbose: print() # Avoids verbose cluttering
        json_file_dict = {
                "filetype": "Json Midi Player",
                "url": "https://github.com/ruiseixasm/JsonMidiPlayer",
                "content": play_list
            }
        # Convert Python dictionary to JSON string
        json_str = json.dumps([ json_file_dict ])

        # Create and start a new thread to run the DLL
        dll_thread = threading.Thread(target=run_dll, args=(json_str, verbose))
        talkie_dll_thread = threading.Thread(target=run_talkie_dll, args=(json_str, talkie_delay_ms, verbose))
        
        dll_thread.start()
        talkie_dll_thread.start()
        dll_thread.join()  # Wait for the thread to finish

        # # Create and start a new process to run the DLL
        # dll_process = multiprocessing.Process(target=run_dll, args=(json_str, verbose))
        # dll_process.start()
        # dll_process.join()  # Wait for the process to finish

        # try:
        #     # Call the C++ function with the JSON string
        #     lib.PlayList_ctypes(json_str.encode('utf-8'), 1 if verbose else 0)
        # except FileNotFoundError:
        #     print(f"Could not find the library file: {lib_path}")
        # except OSError as e:
        #     print(f"An error occurred while loading the library: {e}")
        # except AttributeError as e:
        #     print(f"An error occurred while accessing the function: {e}")
        # except Exception as e:
        #     print(f"An unexpected error occurred when calling the function 'PlayList_ctypes': {e}")



def saveMidiFile(midi_list: list[dict], filename="output.mid"):
    
    # Define ANSI escape codes for colors
    RED = "\033[91m"
    RESET = "\033[0m"
            
    try:
        # pip install midiutil
        from midiutil import MIDIFile
    except ImportError:
        print(f"{RED}Error: The 'midiutil' library is not installed.\033[0m")
        print("Please install it by running 'pip install midiutil'.")
        return
    
    processed_events: list[dict] = []
    # Starts by validating all events by time
    for event in midi_list:
        if all(key in event for key in ("event", "track", "track_name", "tempo", "time", "channel")) \
            and isinstance(event["track"], int) and isinstance(event["time"], (float, int)) \
            and event["track"] >= 0 and event["time"] >= 0:

            processed_events.append(event)
        else:
            print("\033[93mWarning: Some midi events aren't valid!\033[0m")
    
    if len(processed_events) > 0:
        processed_events = sorted(processed_events, key=lambda x: (x["track"], x["time"]))

        midi_tracks: set[int] = set()
        for event in processed_events:
            midi_tracks.add(event["track"]) # sets don't allow duplicates
        MyMIDI = MIDIFile(len(midi_tracks))

        last_event: dict = {
            "track":        -1,
            "tempo":        -1,
            "numerator":    -1,
            "denominator":  -1
        }
        for event in processed_events:
            if event["track"] != last_event["track"]:  # events already sorted (processed)
                if isinstance(event["track_name"], str):
                    MyMIDI.addTrackName(
                        event["track"],
                        event["time"],
                        event["track_name"]
                    )
                else:
                    print("Error, Track name is NOT a string!")
            if event["track"] != last_event["track"] or event["tempo"] != last_event["tempo"]:  # events already sorted (processed)
                if isinstance(event["tempo"], (float, int)):
                    last_event["tempo"] = event["tempo"]
                    MyMIDI.addTempo(
                        event["track"],
                        event["time"],
                        event["tempo"]
                    )
                else:
                    print(f"{RED}Error: Tempo is NOT a number!")
            if all(key in event for key in ("numerator", "denominator")):
                if event["track"] != last_event["track"] \
                    or event["numerator"] != last_event["numerator"] or event["denominator"] != last_event["denominator"]:

                    if isinstance(event["numerator"], int) and isinstance(event["denominator"], int) \
                        and event["numerator"] > 0 and event["denominator"] > 0:

                        last_event["numerator"] = event["numerator"]
                        last_event["denominator"] = event["denominator"]
                        MyMIDI.addTimeSignature(
                            event["track"],
                            event["time"],
                            event["numerator"],
                            int(math.log2(event["denominator"])),
                            24, 8
                        )
                    else:
                        print(f"{RED}Error: Time Signature with wrong values!\033[0m")

            last_event["track"] = event["track"]

            match event["event"]:
                case "Note":
                    if isinstance(event["duration"], (float, int)) and event["duration"] > 0:
                        if 0 <= event["channel"] < 16:
                            if 0 <= event["pitch"] < 128:
                                if 0 <= event["velocity"] < 128:
                                    MyMIDI.addNote(
                                        event["track"],
                                        event["channel"],
                                        event["pitch"],
                                        event["time"],
                                        event["duration"],
                                        event["velocity"]
                                    )
                                else:
                                    print(f"{RED}Error: Note Velocity with wrong values! ({event['velocity']})\033[0m")
                            else:
                                print(f"{RED}Error: Note Pitch with wrong values! ({event['pitch']})\033[0m")
                        else:
                            print(f"{RED}Error: Note Channel with wrong values! ({event['channel']})\033[0m")
                    else:
                        print(f"{RED}Error: Note Duration must be above zero! ({event['duration']})\033[0m")
                case "ControllerEvent":
                    if 0 <= event["channel"] < 16:
                        if 0 <= event["number"] < 128:
                            if 0 <= event["value"] < 128:
                                MyMIDI.addControllerEvent(
                                    event["track"],
                                    event["channel"],
                                    event["time"],
                                    event["number"],
                                    event["value"]
                                )
                            else:
                                print(f"{RED}Error: CC Value with wrong values! ({event['value']})\033[0m")
                        else:
                            print(f"{RED}Error: CC Number with wrong values! ({event['number']})\033[0m")
                    else:
                        print(f"{RED}Error: CC Channel with wrong values! ({event['channel']})\033[0m")
                case "PitchWheelEvent":
                    if 0 <= event["channel"] < 16:
                            if -8192 <= event["value"] < 8192:
                                MyMIDI.addPitchWheelEvent(
                                    event["track"],
                                    event["channel"],
                                    event["time"],
                                    event["value"]
                                )
                            else:
                                print(f"{RED}Error: Pitch Value with wrong values! ({event['value']})\033[0m")
                    else:
                        print(f"{RED}Error: Pitch Channel with wrong values! ({event['channel']})\033[0m")
                case "ChannelPressure":
                    if 0 <= event["channel"] < 16:
                        if 0 <= event["pressure"] < 128:
                            MyMIDI.addChannelPressure(
                                event["track"],
                                event["channel"],
                                event["time"],
                                event["pressure"]
                            )
                        else:
                            print(f"{RED}Error: Channel Pressure Value with wrong values! ({event['pressure']})\033[0m")
                    else:
                        print(f"{RED}Error: Channel Pressure Channel with wrong values! ({event['channel']})\033[0m")
                case "ProgramChange":
                    if 0 <= event["channel"] < 16:
                        if 0 <= event["program"] < 128:
                            MyMIDI.addProgramChange(
                                event["track"],
                                event["channel"],
                                event["time"],
                                event["program"]
                            )
                        else:
                            print(f"{RED}Error: Program Change Program with wrong values! ({event['program']})\033[0m")
                    else:
                        print(f"{RED}Error: Program Change Channel with wrong values! ({event['channel']})\033[0m")
        with open(filename, "wb") as output_file:   # opened to write in binary mode
            MyMIDI.writeFile(output_file)



class Timer:
    def __init__(self):
        self.start_time = None
        self.total_time = 0.0
        self._last_time = None
        self._total_calls = 0

    def call_timer_a(self):
        self._total_calls += 1
        if self.start_time is None:
            self._last_time = self.start_time = time.perf_counter()
        else:
            self._last_time = time.perf_counter()

    def call_timer_b(self):
        elapsed = time.perf_counter() - self._last_time
        self.total_time += elapsed

    def start(self):
        """Start the timer."""
        if self.start_time is not None:
            raise RuntimeError("Timer is already running. Stop it before starting again.")
        self.start_time = time.perf_counter()

    def stop(self):
        """Stop the timer and accumulate the elapsed time."""
        if self.start_time is None:
            raise RuntimeError("Timer is not running. Start it before stopping.")
        elapsed = time.perf_counter() - self.start_time
        self.total_time += elapsed
        self.start_time = None

    def reset(self):
        """Reset the timer."""
        self.start_time = None
        self.total_time = 0.0

    def get_total_time(self):
        """Get the total accumulated time."""
        return self.total_time

    def __str__(self) -> str:
        if self.start_time:
            total_run_time = time.perf_counter() - self.start_time
            return f"Profiling time of {(self.get_total_time() * 1000):.0f} ms " \
                + f"in a total of {(total_run_time * 1000):.0f} ms ({(self.get_total_time() / total_run_time * 100):.2f}%) " \
                + f"| Called {self._total_calls} times ({(self.get_total_time() * 1000 / self._total_calls):.3f} ms per call)"
        return f"ZERO CALLS!"

profiling_timer = Timer()

        # c.profiling_timer.call_timer_a()
        # c.profiling_timer.call_timer_b()
        # print(c.profiling_timer)

def chat_gpt_solution(midi_list: list[dict], filename="output.mid"):
    try:
        # Importing mido for MIDI file processing
        from mido import MidiFile, MidiTrack, Message, MetaMessage
    except ImportError:
        print("Error: The 'mido' library is not installed.")
        print("Please install it by running 'pip install mido'.")
        return

    # Initialize the MIDI file
    midi_file = MidiFile()
    
    # Dictionary to store tracks by their track number
    track_dict = {}
    processed_events = []

    # Validate and process each event
    for event in midi_list:
        if all(key in event for key in ("event", "track", "time", "channel")) \
                and isinstance(event["track"], int) and isinstance(event["time"], (int, float)) \
                and event["track"] >= 0 and event["time"] >= 0:
            processed_events.append(event)

    # Sort events by track and time for proper ordering
    processed_events = sorted(processed_events, key=lambda x: (x["track"], x["time"]))

    # Initialize unique tracks and store them in track_dict
    for event in processed_events:
        track_num = event["track"]
        if track_num not in track_dict:
            # Create a new MidiTrack object for each unique track number
            track = MidiTrack()
            midi_file.tracks.append(track)  # Add new track to the MIDI file
            track_dict[track_num] = track  # Map track number to the MidiTrack object

            # If track_name exists, add it to the track
            if "track_name" in event:
                track.append(MetaMessage('track_name', name=event["track_name"], time=0))

    last_event = {"track": -1, "tempo": None, "time_signature": None}

    # Process each event and add it to the corresponding track
    for event in processed_events:
        track_num = event["track"]
        track = track_dict[track_num]  # Retrieve the MidiTrack object for this track number

        # Tempo setting if provided and different from last set tempo
        if "tempo" in event and (last_event["track"] != track_num or last_event["tempo"] != event["tempo"]):
            track.append(MetaMessage('set_tempo', tempo=int(60000000 / event["tempo"]), time=event["time"]))
            last_event["tempo"] = event["tempo"]

        # Time signature if provided
        if "numerator" in event and "denominator" in event:
            if last_event["track"] != track_num or \
                    last_event["time_signature"] != (event["numerator"], event["denominator"]):
                track.append(MetaMessage(
                    'time_signature',
                    numerator=event["numerator"],
                    denominator=event["denominator"],
                    clocks_per_click=24,
                    time=event["time"]
                ))
                last_event["time_signature"] = (event["numerator"], event["denominator"])

        # Process different event types
        match event["event"]:
            case "Note":
                # Start note (note_on)
                track.append(Message(
                    'note_on',
                    channel=event["channel"],
                    note=event["pitch"],
                    velocity=event["velocity"],
                    time=event["time"]
                ))
                # End note (note_off), time calculated from duration
                track.append(Message(
                    'note_off',
                    channel=event["channel"],
                    note=event["pitch"],
                    velocity=0,
                    time=event["duration"]
                ))
            case "ControllerEvent":
                track.append(Message(
                    'control_change',
                    channel=event["channel"],
                    control=event["number"],
                    value=event["value"],
                    time=event["time"]
                ))
            case "PitchWheelEvent":
                track.append(Message(
                    'pitchwheel',
                    channel=event["channel"],
                    pitch=event["value"],
                    time=event["time"]
                ))
            case "ChannelPressure":
                track.append(Message(
                    'aftertouch',
                    channel=event["channel"],
                    value=event["pressure"],
                    time=event["time"]
                ))
            case "ProgramChange":
                track.append(Message(
                    'program_change',
                    channel=event["channel"],
                    program=event["program"],
                    time=event["time"]
                ))

        # Update the last event's track number
        last_event["track"] = track_num

    # Write the MIDI file to disk
    midi_file.save(filename)



# # Main guard to prevent multiprocessing errors
# if __name__ == "__main__":
#     # Optional: Call freeze_support() for frozen executables
#     multiprocessing.freeze_support()




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