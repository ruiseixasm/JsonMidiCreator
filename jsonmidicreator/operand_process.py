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
# Example using typing.Union (compatible with Python < 3.10)
from typing import Union, TypeVar, TYPE_CHECKING, Type, Callable, List, Tuple, Optional, Any, Generic
from typing import Self

from fractions import Fraction
import json
import enum
import math
# Json Midi Creator Libraries
from . import creator as c
from . import operand as o

from . import operand_label as ol
from . import operand_data as od
from . import operand_unit as ou
from . import operand_rational as ra
from . import operand_generic as og
from . import operand_element as oe
from . import operand_container as oc
from . import operand_frame as of
from . import operand_chaos as ch
from . import operand_tamer as ot
from . import operand_transform as tr
from . import operand_iterations as oi



class Process(o.Operand):
    """`Process`

    A `Process` is target to an `Element` or a `Clip` which result in a output of their data.
    """
    def process(self, operand: o.T) -> o.T:
        return operand  # No copy

    def __rrshift__(self, operand: o.T) -> o.T:
        return self.process(operand)   # No copy (read-only) !



class Save(Process):
    """`Generic -> Process -> Save`

    Saves all parameters' `Serialization` of a given `Operand` into a file.

    Parameters
    ----------
    None, str() : The filename of the Operand's serialization data.
    False, bool() : Include the global settings.
    """
    def __init__(self, filename: str | None = None, include_settings = False):
        super().__init__()
        self.filename = filename
        self.include_settings = include_settings

    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            file_path: str = self.filename
            if not isinstance(file_path, str):
                if isinstance(operand, oc.Composition):
                    file_path = operand.composition_filename() + "_save.json"
                else:
                    file_path = "json/_Save_jsonMidiCreator.json"
            else: # Folder is just a prefix
                file_path = file_path
            c.saveJsonMidiCreator(operand.getSerialization(), file_path, self.include_settings)
            return operand
        return super().__rrshift__(operand)



class Export(Process):
    """`Generic -> Process -> Export`

    Exports a file playable by the `JsonMidiPlayer` program.

    Parameters
    ----------
    None, str() : The filename of the JsonMidiPlayer playable file.
    """
    def __init__(self, filename: str | None = None):
        super().__init__()
        self.filename = filename

    def process(self, operand: o.T) -> o.T:
        match operand:
            case oc.Composition():
                if operand._items:
                    file_path: str = self.filename
                    if not isinstance(file_path, str):
                        file_path = operand.composition_filename() + "_export.json"
                    else: # Folder is just a prefix
                        file_path = file_path
                    composition_length: ra.Length = operand % ra.Length()
                    composition_length_beats: Fraction = composition_length._rational   # Implicit rounding
                    clocking: dict[str, list] = og.settings.getClocking(composition_length_beats)
                    playlist: list[dict] = operand.getPlaylist()
                    c.exportJsonMidiPlay(clocking, playlist, file_path)
                else:
                    print(f"Warning: Trying to export an **empty** list!")
                return operand
            case oe.Element():
                if not isinstance(file_path, str):
                    file_path = "json/_Export_jsonMidiPlayer.json"
                element_length: ra.Length = operand % ra.Length()
                element_length_beats: Fraction = element_length.roundBeats() % Fraction()
                clocking: dict[str, list] = og.settings.getClocking(element_length_beats)
                playlist: list[dict] = operand.getPlaylist()
                c.exportJsonMidiPlay(clocking, playlist, file_path)
                return operand

            case _:
                return super().__rrshift__(operand)



class Render(Process):
    """`Generic -> Process -> Render`

    Renders a midi file playable by any Midi player.

    Parameters
    ----------
    None, str() : The filename of the Midi playable file.
    """
    def __init__(self, filename: str | None = None):
        super().__init__()
        self.filename = filename

    def process(self, operand: o.T) -> o.T:
        # filepath and filename
        file_path: str = self.filename
        if not isinstance(file_path, str):
            if isinstance(operand, oc.Composition):
                file_path = operand.composition_filename() + "_render.mid"
            else:
                file_path = "midi/_MidiExport_song.mid"
        else: # Folder is just a prefix
            file_path = file_path
        # Rendering of the midi file
        match operand:
            case oc.Composition() | oe.Element():
                c.renderMidiFile(operand.getMidilist(), file_path)
                return operand
            case od.Line():
                line_clip = oc.Clip(operand)
                self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
        return super().__rrshift__(operand)



# Define ANSI escape codes for colors
RED = "\033[91m"
RESET = "\033[0m"
        
try:
    # pip install matplotlib
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.backend_bases import MouseEvent
    from matplotlib.widgets import Button
    import matplotlib.patheffects as patheffects
except ImportError:
    print(f"{RED}Error: The 'matplotlib.pyplot' library is not installed.{RESET}")
    print("Please install it by running 'pip install matplotlib'.")
try:
    # pip install numpy
    import numpy as np
except ImportError:
    print(f"{RED}Error: The 'numpy' library is not installed.{RESET}")
    print("Please install it by running 'pip install numpy'.")



class Plot(Process):
    """`Generic -> Process -> Plot`

    Plots the `Composition` content, Notes or the `Automation` if existent.

    Notes
    -----
    - The plotted `T` marks the Tonic Key of the Key Signature with the respective Sharps(#) or Flats(b)
    on the Y-axis, and they concern the immediate following Measures;
    - The Notes' Sharps and Flats plotted concern the Key Signature being used and NOT necessarily
    the Major Scale, in other words, they concern the `Degree` and NOT the `Key`.
        
    Args
    ----
    by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
    block (bool): Suspends the program until the chart is closed.
    pause (float): Sets a time in seconds before the chart is closed automatically.
    iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
        this is dependent on a n_button being given.
    n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
    composition (Composition): A composition to be played together with the plotted one.
    title (str): A title to give to the chart in order to identify it.
    """
    def __init__(self, by_channel: bool = False, block: bool = True, transform: tr.Transform = None,
                 composition: Optional['oc.Composition'] = None, title: str | None = None):
        super().__init__()
        self.by_channel = by_channel
        self.block = block
        self.transform = transform
        self.composition = composition
        self.title = title

        self._compositions: list[oc.Composition] = []
        self._plot_lists: list[list] = []
        self._plot_checksums: list[str] = []
        self._iteration_index: int = 0
        self._n_function: Callable[[int], 'oc.Clip'] = None


    def process(self, operand: o.T) -> 'oc.Composition':
        match operand:
            case oc.Composition():
                return self.plot_composition(operand)
            case oe.Element():
                element_clip = oc.Clip(operand)
                return self.__rrshift__(element_clip)
            case od.Line():
                line_clip = oc.Clip(operand)
                return self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
            case og.Scale():
                og.Scale.plot(self.block, operand % list())
            case ou.KeySignature():
                og.Scale.plot(self.block, operand % list(), operand % ou.Key(), operand % str())
            case oi.Iterations():
                if not isinstance(self.title, str):
                    self.title = operand.__class__.__name__
                self._n_function = operand.n_function
                return self.plot_iterations()
            case _:
                if isinstance(operand, Callable):
                    self._n_function = operand
                    return self.plot_iterations()
        return operand


    _channel_colors = [
        "#4CAF50",  # Green (starting point)    01
        "#2196F3",  # Blue                      02
        "#FF5722",  # Orange                    03
        "#9C27B0",  # Purple                    04
        "#FFEB3B",  # Bright Yellow             05
        "#FF9800",  # Amber                     06
        "#E91E63",  # Pink                      07
        "#00BCD4",  # Cyan                      08
        "#C7E99B",  # Light Green               09
        "#FFC107",  # Gold                      10
        "#4A5ED3",  # Indigo                    11
        "#FF5252",  # Light Red                 12
        "#2B184D",  # Deep Purple               13
        "#CDDC39",  # Lime                      14
        "#03A9F4",  # Light Blue                15
        "#FF4081",  # Hot Pink                  16
    ]

    _white_key_heigh: float = 1.0
    _black_key_heigh: float = 1.0
    _b3_key_heigh: float = 1.0
    _c4_key_heigh: float = 1.0
    _octave_heigh: float = 7 * _white_key_heigh + 5 * _black_key_heigh
    _white_above_black_heigh: float = _white_key_heigh - _black_key_heigh
    _previous_black_keys: tuple[int] = (0, 0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5)

    @staticmethod
    def _pitch_to_y(pitch: float) -> float:
        y: float = 0.0
        pitch_int: int = int(pitch)
        octaves: int = pitch_int // 12
        y += octaves * oc.Composition._octave_heigh
        if pitch_int > 59:
            y += oc.Composition._b3_key_heigh - oc.Composition._white_key_heigh
            if pitch_int > 60:
                y += oc.Composition._c4_key_heigh - oc.Composition._white_key_heigh
        pitch_octave: int = pitch_int % 12
        y += pitch_octave * oc.Composition._white_key_heigh
        y -= oc.Composition._previous_black_keys[pitch_octave] * oc.Composition._white_above_black_heigh
        key_float: float = pitch - pitch_int
        key_heigh: float = oc.Composition._white_key_heigh
        if pitch_int == 59:
            key_heigh = oc.Composition._b3_key_heigh
        elif pitch_int == 60:
            key_heigh = oc.Composition._c4_key_heigh
        elif o.is_black_key(pitch_int):
            key_heigh = oc.Composition._black_key_heigh
        y += key_heigh * key_float
        return y

    @staticmethod
    def _y_to_pitch(y: float) -> float:
        pitch: float = 0.0
    
        return pitch


    def _plot_elements(self):
        """
        The method that does the heavy work of plotting
        """
        # The plotting is managed by the single and original Composition.
        plotlist: list[dict] = self._plot_lists[self._iteration_index]
        composition: oc.Composition = self._compositions[self._iteration_index]
        length_beats: int = composition % ra.Length() % ra.Beats() % int()
        time_signature = composition._get_time_signature()
        checksum_str: str = self._plot_checksums[self._iteration_index]

        self._ax.clear()

        beats_per_measure: Fraction = time_signature % ra.BeatsPerMeasure() % Fraction()
        quantization_beats: Fraction = og.settings._quantization    # Quantization is a Beats value already
        steps_per_measure: Fraction = beats_per_measure / quantization_beats

        chart_title: str = f"{self.title + " - " if self.title != "" else ""}" \
                        + f"{self._compositions[self._iteration_index].__class__.__name__}"
        # Chart title (TITLE)
        if isinstance(self, oc.Section):
            measure_position: int = int(self._position_beats / beats_per_measure)
            chart_title += f"({measure_position}) - "
        else:
            chart_title += " - "
        chart_title += f"{"Masked - " if self._compositions[self._iteration_index].is_masked() else ""}"
        if self._n_function is not None or isinstance(self.transform, tr.Transform):
            chart_title += f"Iteration {self._iteration_index} of {len(self._compositions) - 1} - "
        chart_title += f"({checksum_str})"
        self._ax.set_title(chart_title)

        # Horizontal X-Axis, Time related (COMMON)

        composition_tempo: float = 120.0    # JUST TO MAKE SURE IT WORKS
        if og.settings._tempos:
            composition_tempo = og.settings._tempos[0] % float()

        # # 1. Disable autoscaling and force limits
        # self._ax.set_autoscalex_on(False)
        # current_min, current_max = self._ax.get_xlim()
        # self._ax.set_xlim(current_min, current_max * 1.03)
        self._ax.margins(x=0)  # Ensures NO extra padding is added on the x-axis

        # # By default it's 1 Measure long
        # last_position: Fraction = beats_per_measure
        # last_position_measures: Fraction = last_position / beats_per_measure
        # last_position_measure: int = int(last_position / beats_per_measure)
        # if last_position_measure != last_position_measures:
        #     last_position_measure += 1

        # No content assumed
        last_position: Fraction = Fraction(0)   # No content assumed
        last_position_measures: Fraction = last_position
        last_position_measure: int = 0


        # Vertical Y-Axis, Pitch/Value related (SPECIFIC)
        plot_channels: list[dict] = [ channel_dict["channels"] for channel_dict in plotlist if "channels" in channel_dict ]

        note_channels: list[int] = []
        automation_channels: list[int] = []

        for element_channel in plot_channels:
            for note_channel in element_channel["note"]:
                if note_channel not in note_channels:
                    note_channels.append(note_channel)
            for automation_channel in element_channel["automation"]:
                if automation_channel not in automation_channels:
                    automation_channels.append(automation_channel)

                    
        # Plot Notes
        if note_channels or not automation_channels:

            # As Channels (Drums)
            if self.by_channel:
                self._ax.set_ylabel("Channels")

                # Set MIDI channel ticks with Middle C in bold
                self._ax.set_yticks(range(17))  # Needs to accommodate all labels, so, it's 17
                self._ax.tick_params(axis='y', which='both', length=0)
                y_labels = ['R'] + [
                    channel_0 + 1 for channel_0 in range(16)
                ]
                self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')
                self._ax.set_ylim(0 - 0.5, 16 + 0.5)  # Ensure all channels fit

                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Channel = {round(y)}"
                )

                # Shade Odd Channels (1 based) VERTICAL AXIS
                for channel_0 in range(16):
                    if channel_0 % 2 == 1:
                        self._ax.axhspan(channel_0 - 0.5, channel_0 + 0.5, color='lightgray', alpha=0.5)

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # Plot notes
                    for channel_0 in note_channels:
                        channel_color = Plot._channel_colors[channel_0]
                        channel_plotlist = [
                            channel_note for channel_note in note_plotlist
                            if channel_note["channel"] == channel_0
                        ]

                        for note in channel_plotlist:
                            if type(note["self"]) is oe.Rest:
                                # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                                color_alpha: float = 1.0
                                if note["masked"]:
                                    color_alpha = 0.2
                                self._ax.barh(y = 0.0, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                    height=0.30, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                            else:
                                bar_hatch: str = ''
                                line_style: str = 'solid'
                                if isinstance(note["self"], oe.KeyScale):
                                    line_style = 'dashed'
                                elif isinstance(note["self"], (oe.Rhythm, oe.Tuplet)):
                                    line_style = 'dotted'
                                edge_color: str = 'black'
                                if not note["enabled"]:
                                    edge_color = 'white'

                                color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)

                                if note["velocity"] > 127:
                                    edge_color = 'red'
                                    color_alpha = 1.0
                                elif note["velocity"] < 0:
                                    edge_color = 'blue'
                                    color_alpha = 1.0

                                if note["masked"]:
                                    color_alpha = 0.2
                                    
                                self._ax.barh(y = note["channel"] + 1, width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                        height=0.3, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                                info: str = ""
                                if note["self"]._tied:
                                    info += " Tied"
                                if isinstance(note["self"]._note_effect, og.NoteEffect):
                                    info += " FX"
                                self._ax.text(float(note["position_on"]), note["pitch"] + 0.3, info, ha='left', va='bottom', fontsize=4,
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                    alpha=color_alpha)
                        
                                if "middle_pitch" in note:
                                    self._ax.hlines(y=note["channel"] + 1, xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                    color='black', linewidth=0.5, alpha=color_alpha)
                                    
                else:  # Empty watermark
                    # Add watermark text in the center of the plot
                    self._ax.text(0.5, 0.5, 'EMPTY', 
                                transform=self._ax.transAxes,
                                fontsize=20,
                                color='gray',
                                alpha=0.5,
                                ha='center',
                                va='center',
                                fontweight='bold',
                                fontstyle='italic')
                    
                    # Optional: Add a subtle rectangle watermark
                    self._ax.axhspan(-0.5, 16.5, color='lightgray', alpha=0.1)
                
            # As Chromatic keys (Notes)
            else:

                self._ax.set_ylabel("Chromatic Keys")
                # Where the corner Coordinates are defined
                self._ax.format_coord = lambda x, y: (
                    f"Time = {int(x / composition_tempo * 60 // 60)}'"
                    f"{int(x / composition_tempo * 60 % 60)}''"
                    f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                    f"Measure = {int(x / beats_per_measure)}, "
                    f"Beat = {int(x % beats_per_measure)}, "
                    f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                    f"Pitch = {int(y + 0.5)}"
                )

                # Solid line at y = 60 the Middle C
                self._ax.axhline(y=60 - 0.5, color='gray', linestyle='-', linewidth=1.0)

                note_plotlist: list[dict] = [ element_dict["note"] for element_dict in plotlist if "note" in element_dict ]

                if note_plotlist:

                    # Updates X-Axis data
                    last_position = max(note["position_off"] for note in note_plotlist)
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # PITCHES VERTICAL AXIS

                    # Get pitch range
                    min_pitch: int = int(min(note["pitch"] for note in note_plotlist) // 12 * 12)
                    max_pitch: int = int(max(note["pitch"] for note in note_plotlist) // 12 * 12 + 12)

                else:  # Empty watermark

                    # Updates X-Axis data
                    last_position_measures = last_position / beats_per_measure
                    last_position_measure = int(last_position_measures) # Trims extra length
                    if last_position_measure != last_position_measures: # Includes the trimmed length
                        last_position_measure += 1  # Adds only if the end doesn't coincide

                    # PITCHES VERTICAL AXIS

                    # Get pitch range
                    min_pitch: int = 60
                    max_pitch: int = 60

                    # Add watermark text in the center of the plot
                    self._ax.text(0.5, 0.5, 'EMPTY', 
                                transform=self._ax.transAxes,
                                fontsize=20,
                                color='gray',
                                alpha=0.5,
                                ha='center',
                                va='center',
                                fontweight='bold',
                                fontstyle='italic')
                    
                    # Optional: Add a subtle rectangle watermark
                    self._ax.axhspan(-0.5, 16.5, color='lightgray', alpha=0.1)


                pitch_range: int = max_pitch - min_pitch
                if pitch_range // 12 < 4:   # less than 4 octaves
                    middle_c_reference: int = 60    # middle C pitch
                    extra_octaves_range: int = 4 - pitch_range // 12
                    for _ in range(extra_octaves_range):
                        raised_top: int = max_pitch + 12
                        lowered_bottom: int = min_pitch - 12
                        if abs(raised_top - middle_c_reference) < abs(lowered_bottom - middle_c_reference):
                            max_pitch += 12
                        else:
                            min_pitch -= 12

                # Set MIDI note ticks with Middle C in bold
                self._ax.set_yticks(range(min_pitch, max_pitch + 1))
                self._ax.tick_params(axis='y', which='both', color='white')

                # # Only show tick marks for octaves (pitch % 12 == 0)
                # for tick in self._ax.yaxis.get_major_ticks():
                #     if tick.get_loc() % 12 != 0:  # If not an octave
                #         tick.tick1line.set_visible(False)  # Hide left tick
                #         tick.tick2line.set_visible(False)  # Hide right tick

                # Where the VERTICAL axis is defined - Chromatic Keys
                chromatic_keys: list[str] = ["C", "", "D", "", "E", "F", "", "G", "", "A", "", "B"]
                
                y_labels = [
                    chromatic_keys[pitch % 12] + (str(pitch // 12 - 1) if pitch % 12 == 0 else "")
                    for pitch in range(min_pitch, max_pitch + 1)
                ]  # Bold Middle C
                self._ax.set_yticklabels(y_labels, fontsize=7, fontweight='bold')

                # # Adjust alignment and shift
                # for label in self._ax.get_yticklabels():
                #     label.set_horizontalalignment("right")  # right-align text
                #     label.set_x(-0.005)                     # shift a bit left (tweak as needed)

                self._ax.set_ylim(min_pitch - 0.5, max_pitch + 0.5)  # Ensure all notes fit

                # Shade and shorten black keys and enlarge B3 and C4 keys
                for pitch in range(min_pitch, max_pitch + 1):
                    if o.is_black_key(pitch):   # Make it less taller, 0.6 instead of 1.0
                        self._ax.axhspan(pitch - 0.3, pitch + 0.3, color='lightgray', alpha=0.5)

                staff_modes: dict[int, int] = {}
                staff_tonic_keys: dict[int, int] = {}
                staff_sharps_or_flats: dict[int, list[int]] = {}

                # Plot notes per Channel
                for channel_0 in note_channels:
                    printed_channel_number: bool = False
                    channel_color = Plot._channel_colors[channel_0]
                    channel_plotlist = [
                        channel_note for channel_note in note_plotlist
                        if channel_note["channel"] == channel_0
                    ]
                    last_mode_measure: int = -1         # Tracker
                    last_tonic_key_measure: int = -1
                    last_sharps_or_flats_measure: int = -1

                    for note in channel_plotlist:
                        if isinstance(note["self"], oe.Rest):
                            # Available hatch patterns: '/', '\\', '|', '-', '+', 'x', 'o', 'O', '.', '*'
                            color_alpha: float = 1.0
                            if note["masked"]:
                                color_alpha = 0.2
                            self._ax.barh(y = note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]),
                                height=0.40, color='none', hatch='', edgecolor='black', linewidth=1.0, linestyle='solid', alpha = color_alpha)
                        else:
                            if o.is_black_key(round(note["pitch"])):
                                bar_height: float = 0.25
                            else:
                                bar_height: float = 0.40
                            bar_hatch: str = ''
                            line_style: str = 'solid'
                            if isinstance(note["self"], oe.KeyScale):
                                line_style = 'dashed'
                            elif isinstance(note["self"], oe.Tuplet):
                                line_style = 'dotted'
                            edge_color: str = 'black'
                            if not note["enabled"]:
                                edge_color = 'white'

                            color_alpha: float = round(0.3 + 0.7 * (note["velocity"] / 127), 2)
                            if note["velocity"] > 127:
                                edge_color = 'red'
                                color_alpha = 1.0
                            elif note["velocity"] < 0:
                                edge_color = 'blue'
                                color_alpha = 1.0
                            
                            if note["masked"]:
                                color_alpha = 0.2

                            self._ax.barh(y=note["pitch"], width = float(note["position_off"] - note["position_on"]), left = float(note["position_on"]), 
                                    height=bar_height, color=channel_color, hatch=bar_hatch, edgecolor=edge_color, linewidth=1.0, linestyle=line_style, alpha=color_alpha)

                            info: str = ""
                            if note["self"]._tied:
                                info += " Tied"
                            if isinstance(note["self"]._note_effect, og.NoteEffect):
                                info += " FX"
                            self._ax.text(float(note["position_on"]), note["pitch"] + 0.3, info, ha='left', va='bottom', fontsize=4,
                                color='black',  # Outline color
                                path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                alpha=color_alpha)
                        
                            if "middle_pitch" in note:
                                self._ax.hlines(y=note["middle_pitch"], xmin=float(note["position_on"]), xmax=float(note["position_off"]), 
                                                color='black', linewidth=0.5, alpha=color_alpha)

                            # note Measures to keep track of
                            note_measure: int = int(note["position_on"] // beats_per_measure)
                            flag_update_key_signature: bool = False

                            # Sets the Measure KeySignature if not yet set
                            if note_measure not in staff_modes: # Major, minor, Locrian, etc...

                                # Updates the last_mode_measure (Keeps track of the last measure staff data)
                                changed_last_mode_measure: int = last_mode_measure
                                while changed_last_mode_measure < note_measure and changed_last_mode_measure not in staff_modes:
                                    changed_last_mode_measure += 1
                                if changed_last_mode_measure < note_measure:
                                    last_mode_measure = changed_last_mode_measure
                            
                                mode_0: int = note["mode"]  # Mode here is the same as Major, minor, Locrian, etc...
                                if last_mode_measure < 0 or staff_modes[last_mode_measure] != mode_0:
                                    staff_modes[note_measure] = mode_0  # It's the Note KeySignature that is Plotted
                                    scale_mode: int = mode_0 % 9 + 1
                                    mode_marker: str = og.Scale._names[scale_mode][0]
                                    base_pitch: int = max_pitch - 12
                                    self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + 12, mode_marker, ha='left', va='center', fontsize=6, color='black')
                                    flag_update_key_signature = True
                                    last_mode_measure = note_measure
                            else:
                                last_mode_measure = note_measure

                            if note_measure not in staff_tonic_keys:    # The T marking the Tonic
                                
                                # Updates the last_tonic_key_measure
                                changed_last_tonic_key_measure: int = last_tonic_key_measure
                                while changed_last_tonic_key_measure < note_measure and changed_last_tonic_key_measure not in staff_tonic_keys:
                                    changed_last_tonic_key_measure += 1
                                if changed_last_tonic_key_measure < note_measure:
                                    last_tonic_key_measure = changed_last_tonic_key_measure
                            
                                tonic_key: int = note["tonic_key"]
                                if last_tonic_key_measure < 0 or staff_tonic_keys[last_tonic_key_measure] != tonic_key:
                                    staff_tonic_keys[note_measure] = tonic_key
                                    base_pitch: int = max_pitch - 12
                                    self._ax.text(float(note_measure * beats_per_measure) + 0.05, base_pitch + tonic_key, 'T', ha='left', va='center', fontsize=5, color='black')
                                    flag_update_key_signature = True
                                    last_tonic_key_measure = note_measure
                            else:
                                last_tonic_key_measure = note_measure

                            if note_measure not in staff_sharps_or_flats: # Concerning the KeySignature, sharps, > 0 or flats, < 0, from -7 to +7
                                if flag_update_key_signature:
                                    diatonic_mode_0: int = staff_modes[last_mode_measure]
                                    diatonic_scale: list[int] = og.Scale.get_diatonic_scale(diatonic_mode_0 + 1)
                                    tonic_key: int = staff_tonic_keys[last_tonic_key_measure]
                                    scale_accidentals: list[int] = og.Scale.sharps_or_flats_picker(tonic_key, diatonic_scale)
                                    if last_sharps_or_flats_measure < 0 or staff_sharps_or_flats[last_sharps_or_flats_measure] != scale_accidentals:
                                        staff_sharps_or_flats[note_measure] = scale_accidentals
                                        
                                        for accidental_key, accidental in enumerate(scale_accidentals):
                                            chromatic_pitch: int = base_pitch
                                            if accidental > 0:
                                                accidental_key += 1
                                                chromatic_pitch += accidental_key % 12
                                                self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♯', ha='right', va='center', fontsize=10, fontweight='bold', color='black')
                                            elif accidental < 0:
                                                accidental_key -= 1
                                                chromatic_pitch += accidental_key % 12
                                                self._ax.text(float(note_measure * beats_per_measure) - 0.05, chromatic_pitch, '♭', ha='right', va='center', fontsize=10, fontweight='bold', color='black')

                                        last_sharps_or_flats_measure = note_measure
                            else:
                                last_sharps_or_flats_measure = note_measure


                            # Where the bar accidentals are plotted individually for each Note on the left side of them
                            if note["accidentals"]:
                                symbol: str = ''
                                if note["accidentals"] > 0: # Sharped
                                    symbol = '♯' * note["accidentals"]
                                else:                       # Flattened
                                    symbol = '♭' * (note["accidentals"] * -1)
                                y_pos: int = note["pitch"]
                                x_pos = float(note["position_on"]) - 0.15
                                self._ax.text(x_pos, y_pos, symbol, ha='center', va='center', fontsize=8, fontweight='bold',
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.4, foreground=channel_color)],
                                    alpha=color_alpha)

                            if not printed_channel_number:
                                y_pos: int = note["pitch"] + 0.2
                                x_pos = (float(note["position_on"]) + float(note["position_off"])) / 2
                                self._ax.text(x_pos, y_pos, channel_0 + 1, ha='center', va='bottom', fontsize=8,
                                    color='black',  # Outline color
                                    path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                                    alpha=color_alpha)
                                printed_channel_number = True
                                 
        # Plot Automations
        else:

            self._ax.set_ylabel("Automation Values (MSB)")
            # Where the corner Coordinates are defined
            self._ax.format_coord = lambda x, y: (
                f"Time = {int(x / composition_tempo * 60 // 60)}'"
                f"{int(x / composition_tempo * 60 % 60)}''"
                f"{int(x / composition_tempo * 60_000 % 1000)}ms, "
                f"Measure = {int(x / beats_per_measure)}, "
                f"Beat = {int(x % beats_per_measure)}, "
                f"Step = {int(x / beats_per_measure * steps_per_measure % steps_per_measure)}, "
                f"Value = {int(y + 0.5)}"
            )

            automation_plotlist: list[dict] = [
                    element_dict["automation"] for element_dict in plotlist
                    if "automation" in element_dict and isinstance(element_dict["automation"]["self"], oe.Automatable)
                ]

            if automation_plotlist:

                # Updates X-Axis data
                last_position = max(automation["position_beats"] for automation in automation_plotlist)
                last_position_measures = last_position / beats_per_measure
                last_position_measure = int(last_position_measures)
                if last_position_measure != last_position_measures:
                    last_position_measure += 1

                # Axis limits
                self._ax.set_ylim(-1, 128)
                # Ticks
                self._ax.set_yticks(range(0, 129, 8))

                # Dashed horizontal lines at multiples of 16 (except 64)
                for i in range(0, 129, 16):
                    if i != 64:
                        self._ax.axhline(y=i, color='gray', linestyle='--', linewidth=1)
                # Dashed line at y = 127
                self._ax.axhline(y=127, color='gray', linestyle='--', linewidth=1)
                # Solid line at y = 64
                self._ax.axhline(y=64, color='gray', linestyle='-', linewidth=1.5)

                # Plot automations
                for channel_0 in automation_channels:
                    channel_color = Plot._channel_colors[channel_0]
                    channel_plotlist = [
                        channel_automation for channel_automation in automation_plotlist
                        if channel_automation["channel"] == channel_0
                    ]

                    if channel_plotlist:

                        channel_plotlist.sort(key=lambda a: a['position'])

                        # Plotting point lists
                        x: list[float]  = []
                        y: list[int]    = []
                        for automation in channel_plotlist:
                            x.append( float(automation["position_beats"]) )
                            y.append( automation["value"] )

                        # Stepped line connecting the points
                        self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                        
                        if automation["masked"]:
                            color_alpha = 0.2
                        else:
                            color_alpha = 1.0

                        edge_color: str = 'black'
                        if not automation["enabled"]:
                            edge_color = 'white'
                        
                        # Actual data points
                        marker: str = 'o'
                        info: str = str(channel_0 + 1)
                        match automation["self"]:
                            case oe.ControlChange():
                                info += f".{automation["self"]._controller._number_msb}"
                            case oe.Aftertouch():
                                marker = 'v'
                            case _: # PitchBend
                                marker = 'P'

                        self._ax.plot(x, y, marker=marker, linestyle='None', color=channel_color,
                                    markeredgecolor=edge_color, markeredgewidth=1, markersize=6, alpha = color_alpha)

                        # Add the tailed line up to the end of the chart
                        x = [
                            float(channel_plotlist[-1]["position_beats"]),
                            float(last_position_measure * beats_per_measure)
                        ]
                        y = [
                            channel_plotlist[-1]["value"],
                            channel_plotlist[-1]["value"]
                        ]

                        # Stepped line connecting the points
                        self._ax.plot(x, y, linestyle='-', drawstyle='steps-post', color=channel_color, linewidth=0.5)
                        # Actual data points
                        self._ax.plot(x, y, marker='None', linestyle='None', color=channel_color, markersize=6)

                        y_pos: int = automation["value"] + 2
                        x_pos = automation["position_beats"]
                        self._ax.text(x_pos, y_pos, info, ha='center', va='bottom', fontsize=8,
                            color='black',  # Outline color
                            path_effects=[patheffects.withStroke(linewidth=1.0, foreground=channel_color)],
                            alpha=color_alpha)
                                        

        # Draw vertical grid lines based on beats and measures
        one_extra_subdivision: float = quantization_beats
        four_measures_multiple: int = max(4, (last_position_measure - 1) // 4 * 4 + 4)
        step_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(quantization_beats))
        beat_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), 1)
        measure_positions = np.arange(0.0, float(four_measures_multiple * beats_per_measure + one_extra_subdivision), float(beats_per_measure))
    
        for measure_pos in measure_positions:
            self._ax.axvline(measure_pos, color='black', linestyle='-', alpha=1.0, linewidth=0.7)   # Measure lines
        for beat_pos in beat_positions:
            self._ax.axvline(beat_pos, color='gray', linestyle='-', alpha=0.5, linewidth=0.5)       # Beat lines
        for grid_pos in step_positions:
            self._ax.axvline(grid_pos, color='gray', linestyle='dotted', alpha=0.25, linewidth=0.5) # Step subdivisions

        # Set x-axis labels in 'Measure.Beat' format
        measure_labels = [
            f"{int(pos // float(beats_per_measure))}" for pos in measure_positions
        ]
        
        self._ax.set_xlabel(
            f"Measures played at {round(composition_tempo, 1)}bpm for "
            f"{int(length_beats / composition_tempo * 60 // 60)}'"
            f"{int(length_beats / composition_tempo * 60 % 60)}''"
            f"{int(length_beats / composition_tempo * 60_000 % 1000)}ms "
            f"with a Length of {length_beats} Beats "
            f"a Time Signature of {time_signature._top}/{time_signature._bottom} "
            f"and a Quantization of {quantization_beats} Beat"
        )

        self._ax.set_xticks(measure_positions)  # Only show measure & beat labels
        if four_measures_multiple > 100:
            self._ax.set_xticklabels(measure_labels, fontsize=6, rotation=45)
        else:
            self._ax.set_xticklabels(measure_labels, rotation=0)
        self._fig.canvas.draw_idle()

        return None


    def _run_play(self, even = None, loops: int = 1) -> Self:
        import threading
        iteration_self: oc.Composition = self._compositions[self._iteration_index]
        threading.Thread(target=Play.play, args=(iteration_self, loops)).start()
        return self

    def _run_composition(self, even = None, loops: int = 1) -> Self:
        import threading
        if isinstance(self.composition, oc.Composition):
            iteration_self: oc.Composition = self._compositions[self._iteration_index]
            iteration_composition: oc.Composition = self.composition + iteration_self
            threading.Thread(target=Play.play, args=(iteration_composition, loops)).start()
        return self

    def _plot_filename(self, composition: 'oc.Composition') -> str:
        # Process title separately (replace whitespace with underscores)
        processed_title = str(self.title).replace(" ", "_").replace("\t", "_").replace("\n", "_").replace("__", "_")
        composition_designations: list[str] = [
            processed_title,
            type(composition).__name__,
            f"{self._iteration_index}",
            f"{len(self._compositions) - 1}",
            o.checksum_to_string(composition.checksum())
        ]
        # 1. Filter empty strings and convert all parts to lowercase
        filtered_strings = [
            designation.strip().lower() 
            for designation in composition_designations 
            if designation
        ]
        # 2. Join with single underscore (no leading/trailing/double underscores)
        return "_".join(filtered_strings)

    def _run_save(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_save.json"
        composition >> Save(file_name)
        return self

    def _run_export(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_export.json"
        composition >> Export(file_name)
        return self

    def _run_render(self, even = None) -> Self:
        composition = self._compositions[self._iteration_index]
        file_name: str = self._plot_filename(composition) + "_render.mid"
        composition >> Render(file_name)
        return self

    @staticmethod
    def _disable_button(button: Button) -> Button:
        # Set disabled style
        button.label.set_color('lightgray')         # Light text
        button.ax.set_facecolor('none')             # No fill color
        button.hovercolor = 'none'
        for spine in button.ax.spines.values():
            spine.set_color('lightgray')
        return button

    @staticmethod
    def _enable_button(button: Button) -> Button:
        # Set enabled style
        button.ax.set_facecolor('white')
        button.hovercolor = 'gray'
        button.label.set_color('black')
        for spine in button.ax.spines.values():
            spine.set_color('black')
        return button

    def _on_move(self, event: MouseEvent) -> Self:
        if event.inaxes == self._ax:
            print(f"x = {event.xdata}, y = {event.ydata}")
        return self

    def _on_key(self, event: MouseEvent) -> Self:
        match event.key:
            case 'ctrl+p' | 'ctrl+enter':
                self._run_play(event, 4)
            case 'p' | 'enter':
                self._run_play(event)
            case 'ctrl+c' | 'ctrl+space' | 'ctrl+ ':
                self._run_composition(event, 4)
            case 'c' | ' ':
                self._run_composition(event)
            case 'S':
                self._run_save(event)
            case 'E':
                self._run_export(event)
            case 'R':
                self._run_render(event)
            case 'n':
                self._run_new(event)
            case ',':
                self._run_previous(event)
            case '.':
                self._run_next(event)
            case 'm':
                self._run_first(event)
            case '/' | "-" | ";":
                self._run_last(event)
        return self
    
    def _onclick(self, event: MouseEvent) -> Self:
        import threading
        if event.button == 3 and event.xdata is not None and event.ydata is not None:   # 1=left, 2=middle, 3=right
            composition = self._compositions[self._iteration_index]
            at_position_elements: list[oe.Element] = composition.at_position_elements(ra.Position(ra.Beats(event.xdata)))
            at_position_notes: list[oe.Note] = [
                single_note.copy() for single_note in at_position_elements
                if isinstance(single_note, oe.Note)
            ]
            if at_position_notes:
                if self.by_channel:
                    if 0 <= round(event.ydata - 1) < 16:
                        # Sort by Position in reverse instead
                        at_position_notes.sort(key=lambda note:note._position_beats * -1)
                        at_position_notes = [ at_position_notes[0] ]    # Just a single note is played
                        at_position_notes[0]._channel_0 = round(event.ydata - 1)
                        at_position_notes[0]._position_beats = Fraction(0)
                    else:
                        return self
                else:
                    # Sort by Pitch instead
                    at_position_notes.sort(key=lambda note:note._pitch.get_absolute_pitch())
                    minimum_position: Fraction = None
                    plotting_pitch: int = int(event.ydata + 0.5)
                    for single_note in at_position_notes:
                        if minimum_position is None:
                            minimum_position = single_note._position_beats
                            root_pitch: int = single_note._pitch.get_absolute_pitch()
                            single_note._pitch << plotting_pitch
                            plotting_pitch -= root_pitch
                        else:
                            if single_note._position_beats < minimum_position:
                                minimum_position = single_note._position_beats
                            single_note._pitch += plotting_pitch
                    for single_note in at_position_notes:
                        single_note._position_beats -= minimum_position
                    
                threading.Thread(target=Play.play, args=(oc.Clip( od.Pipe(at_position_notes) ),)).start()
        return self


    def plot_composition(self, composition: 'oc.Composition') -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            composition (Composition): A composition to be played together with the plotted one.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        # First composition and its plotting (i = 0) it's always the self copy
        self._compositions      = [ composition.copy() ]   # Works with a forced copy (Read Only)
        self._plot_lists        = [ composition.getPlotlist() ]
        self._plot_checksums    = [ o.checksum_to_string(composition.checksum()) ]
        if not isinstance(self.title, str):
            self.title = composition._name

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        # Where the window title is set too
        self._fig, self._ax = plt.subplots(num=self.title, figsize=(12, 6))
        # Replace handler
        try:
            # self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)
            # mpl.rcParams['keymap.back'].remove('left')
            # mpl.rcParams['keymap.forward'].remove('right')

            # Get the current keymap
            current_keymap: list = plt.rcParams['keymap.all_axes']
            # Remove the 'p' key binding
            current_keymap.remove('p')
            current_keymap.remove('s')
            # Update the rcParams
            plt.rcParams['keymap.all_axes'] = current_keymap
        except Exception as e:
            pass    # No need to print anything
            # print(f"Unable to disable default keys!")
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))
        self._fig.canvas.mpl_connect('button_press_event', lambda event: self._onclick(event))

        # Plot the Composition
        self._plot_elements()

        # Where the padding is set
        plt.tight_layout()

        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 3.00  # Where the HATCH thickness is set

        # Play Button Widget
        ax_button = plt.axes([0.979, 0.888, 0.015, 0.05])
        play_button = Button(ax_button, 'P', color='white', hovercolor='grey')
        play_button.on_clicked(self._run_play)

        # Composition Button Widget
        ax_button = plt.axes([0.979, 0.828, 0.015, 0.05])
        composition_button = Button(ax_button, 'C', color='white', hovercolor='grey')
        composition_button.on_clicked(self._run_composition)

        # Previous Button Widget
        ax_button = plt.axes([0.979, 0.768, 0.015, 0.05])
        self._previous_button = Button(ax_button, '<', color='white', hovercolor='grey')
        self._previous_button.on_clicked(self._run_previous)

        # Next Button Widget
        ax_button = plt.axes([0.979, 0.708, 0.015, 0.05])
        self._next_button = Button(ax_button, '>', color='white', hovercolor='grey')
        self._next_button.on_clicked(self._run_next)

        # New Button Widget
        ax_button = plt.axes([0.979, 0.648, 0.015, 0.05])
        new_button = Button(ax_button, 'N', color='white', hovercolor='grey')
        new_button.on_clicked(self._run_new)

        # Buttons are vertically spaced by 0.060

        # Save Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        save_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        save_button.on_clicked(self._run_save)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        render_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        render_button.on_clicked(self._run_render)

        if not isinstance(self.composition, oc.Composition):
            # Composition Button Widget
            self._disable_button(composition_button)

        # Previous Button Widget
        if self._iteration_index == 0:
            self._disable_button(self._previous_button)
        # Next Button Widget
        self._disable_button(self._next_button)

        if not callable(self._n_function) and not isinstance(self.transform, tr.Transform):
            # New Button Widget
            self._disable_button(new_button)

        plt.show(block=self.block)

        return composition
    

    def _run_first(self, even = None) -> Self:
        if self._iteration_index > 0:
            self._iteration_index = 0
            self._plot_elements()
            self._enable_button(self._next_button)
            if self._iteration_index == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_previous(self, even = None) -> Self:
        if self._iteration_index > 0:
            self._iteration_index -= 1
            self._plot_elements()
            self._enable_button(self._next_button)
            if self._iteration_index == 0:
                self._disable_button(self._previous_button)
        return self

    def _run_next(self, even = None) -> Self:
        if self._iteration_index < len(self._plot_lists) - 1:
            self._iteration_index += 1
            self._plot_elements()
            self._enable_button(self._previous_button)
            if self._iteration_index == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self

    def _run_last(self, even = None) -> Self:
        if self._iteration_index < len(self._plot_lists) - 1:
            self._iteration_index = len(self._plot_lists) - 1
            self._plot_elements()
            self._enable_button(self._previous_button)
            if self._iteration_index == len(self._plot_lists) - 1:
                self._disable_button(self._next_button)
        return self


    def _run_new(self, even = None) -> Self:
        if isinstance(self.transform, tr.Transform):
            clip: oc.Composition = self._compositions[-1]    # It has always at least one
            if isinstance(clip, oc.Clip):
                new_iteration = self.transform.next(clip.copy()) # Decouples
                if isinstance(new_iteration, oc.Clip):
                    self._iteration_index = len(self._compositions)
                    plotlist: list[dict] = new_iteration.getPlotlist()
                    new_checksum_str: str = o.checksum_to_string(new_iteration.checksum())
                    self._compositions.append(new_iteration)
                    self._plot_lists.append(plotlist)
                    self._plot_checksums.append(new_checksum_str)
                    self._plot_elements()
                    self._enable_button(self._previous_button)
                    self._disable_button(self._next_button)

        elif callable(self._n_function):
            # Keeps iterating the root/seed composition
            new_iteration: oc.Composition = self._n_function(self._iteration_index + 1)
            if isinstance(new_iteration, oc.Composition):
                self._iteration_index = len(self._compositions)
                plotlist: list[dict] = new_iteration.getPlotlist()
                new_checksum_str: str = o.checksum_to_string(new_iteration.checksum())
                self._compositions.append(new_iteration)
                self._plot_lists.append(plotlist)
                self._plot_checksums.append(new_checksum_str)
                self._plot_elements()
                self._enable_button(self._previous_button)
                self._disable_button(self._next_button)
        return self


    def plot_iterations(self) -> Self:
        """
        Plots the `Note`s in a `Composition`, if it has no Notes it plots the existing `Automation` instead.

        Args:
            by_channel: Allows the visualization in a Drum Machine alike instead of by Pitch.
            block (bool): Suspends the program until the chart is closed.
            pause (float): Sets a time in seconds before the chart is closed automatically.
            iterations (int): Sets the amount of iterations automatically generated on the chart opening, \
                this is dependent on a n_button being given.
            n_button (Callable): A function that takes a Composition to be used to generate a new iteration.
            composition (Composition): A composition to be played together with the plotted one.
            title (str): A title to give to the chart in order to identify it.

        Returns:
            Composition: Returns the presently plotted composition.
        """
        # First composition and its plotting (i = 0) it's always the self copy
        iteration_0: oc.Composition = self._n_function(0)
        self._compositions      = [ iteration_0 ]   # Works with a forced copy (Read Only)
        self._plot_lists        = [ iteration_0.getPlotlist() ]
        self._plot_checksums    = [ o.checksum_to_string(iteration_0.checksum()) ]
        if not isinstance(self.title, str):
            self.title = iteration_0 % str()

        # Enable interactive mode (doesn't block the execution)
        plt.ion()

        # Where the window title is set too
        self._fig, self._ax = plt.subplots(num=self.title, figsize=(12, 6))
        # Replace handler
        try:
            # self._fig.canvas.mpl_disconnect(self._fig.canvas.manager.key_press_handler_id)
            # mpl.rcParams['keymap.back'].remove('left')
            # mpl.rcParams['keymap.forward'].remove('right')

            # Get the current keymap
            current_keymap: list = plt.rcParams['keymap.all_axes']
            # Remove the 'p' key binding
            current_keymap.remove('p')
            current_keymap.remove('s')
            # Update the rcParams
            plt.rcParams['keymap.all_axes'] = current_keymap
        except Exception as e:
            pass    # No need to print anything
            # print(f"Unable to disable default keys!")
        self._fig.canvas.mpl_connect('key_press_event', lambda event: self._on_key(event))
        self._fig.canvas.mpl_connect('button_press_event', lambda event: self._onclick(event))

        # Plot the Composition
        self._plot_elements()

        # Where the padding is set
        plt.tight_layout()

        plt.subplots_adjust(right=0.975)  # 2.5% right padding
        # Avoids too thick hatch lines
        plt.rcParams['hatch.linewidth'] = 3.00  # Where the HATCH thickness is set

        # Play Button Widget
        ax_button = plt.axes([0.979, 0.888, 0.015, 0.05])
        play_button = Button(ax_button, 'P', color='white', hovercolor='grey')
        play_button.on_clicked(self._run_play)

        # Composition Button Widget
        ax_button = plt.axes([0.979, 0.828, 0.015, 0.05])
        composition_button = Button(ax_button, 'C', color='white', hovercolor='grey')
        composition_button.on_clicked(self._run_composition)

        # Previous Button Widget
        ax_button = plt.axes([0.979, 0.768, 0.015, 0.05])
        self._previous_button = Button(ax_button, '<', color='white', hovercolor='grey')
        self._previous_button.on_clicked(self._run_previous)

        # Next Button Widget
        ax_button = plt.axes([0.979, 0.708, 0.015, 0.05])
        self._next_button = Button(ax_button, '>', color='white', hovercolor='grey')
        self._next_button.on_clicked(self._run_next)

        # New Button Widget
        ax_button = plt.axes([0.979, 0.648, 0.015, 0.05])
        new_button = Button(ax_button, 'N', color='white', hovercolor='grey')
        new_button.on_clicked(self._run_new)

        # Buttons are vertically spaced by 0.060

        # Save Button Widget
        ax_button = plt.axes([0.979, 0.528, 0.015, 0.05])
        save_button = Button(ax_button, 'S', color='white', hovercolor='grey')
        save_button.on_clicked(self._run_save)

        # Execution Button Widget
        ax_button = plt.axes([0.979, 0.468, 0.015, 0.05])
        export_button = Button(ax_button, 'E', color='white', hovercolor='grey')
        export_button.on_clicked(self._run_export)

        # Render Button Widget
        ax_button = plt.axes([0.979, 0.408, 0.015, 0.05])
        render_button = Button(ax_button, 'R', color='white', hovercolor='grey')
        render_button.on_clicked(self._run_render)

        if not isinstance(self.composition, oc.Composition):
            # Composition Button Widget
            self._disable_button(composition_button)

        # Previous Button Widget
        if self._iteration_index == 0:
            self._disable_button(self._previous_button)
        # Next Button Widget
        self._disable_button(self._next_button)

        if not callable(self._n_function) and not isinstance(self.transform, tr.Transform):
            # New Button Widget
            self._disable_button(new_button)

        plt.show(block=self.block)

        return self._compositions[self._iteration_index]


    # CHAINABLE OPERATIONS

    def __imul__(self, operand: any) -> Self:
        operand = self._tail_wrap(operand)    # Processes the tailed self operands if existent
        if isinstance(operand, int):
            if callable(self._n_function) and operand > 0:
                for i in range(operand):
                    new_composition: oc.Composition = self._n_function(i)
                    new_plotlist: list[dict] = new_composition.getPlotlist()
                    new_checksum_str: str = o.checksum_to_string(new_composition.checksum())
                    self._compositions.append(new_composition)
                    self._plot_lists.append(new_plotlist)
                    self._plot_checksums.append(new_checksum_str)
                    self._iteration_index += 1
        return self


class Play(Process):
    """`Generic -> Process -> Play`

    Plays an `Element` or a `Composition` straight on into the `JsonMidiPlayer` program.

    Args:
        verbose (bool): Defines the `verbose` mode of the playing.
        plot (bool): Plots a chart before playing it.
        block (bool): Blocks the Plot until is closed and then plays the plotted content.
    """
    def __init__(self, loops: int = 1, verbose: bool = False, plot: bool = False, block: bool = False, talkie_delay_ms: int = 500):
        super().__init__()
        self.loops = loops
        self.verbose = verbose
        self.plot = plot
        self.block = block
        self.talkie_delay_ms = talkie_delay_ms
        

    def process(self, operand: o.T) -> o.T:
        import threading
        match operand:
            case oc.Composition():
                if operand._items:
                    composition_length: ra.Length = operand % ra.Length()
                    composition_length_beats: Fraction = composition_length._rational   # Implicit rounding
                    clocking: dict[str, list] = og.settings.getClocking(composition_length_beats)
                    playlist: list[dict] = operand.getPlaylist()  # Where the heavy lifting method is called
                    if self.plot and self.block:
                        # Start the function in a new process
                        process = threading.Thread(target=c.playJsonMidiPlay,
                                                   args=(clocking, playlist,
                                                         self.loops,
                                                         self.verbose,
                                                         self.talkie_delay_ms))
                        process.start()
                        operand >> Plot(self.block)
                    else:
                        if self.plot and not self.block:
                            operand >> Plot(self.block)
                        c.playJsonMidiPlay(clocking, playlist,
                                            self.loops,
                                            self.verbose,
                                            self.talkie_delay_ms)
                else:
                    print(f"Warning: Trying to play an **empty** list!")
                return operand
            case oe.Element():
                element_length: ra.Length = operand % ra.Length()
                element_length_beats: Fraction = element_length.roundBeats() % Fraction()
                clocking: dict[str, list] = og.settings.getClocking(element_length_beats)
                playlist: list[dict] = operand.getPlaylist()  # Where the heavy lifting method is called
                if self.plot and self.block:
                    # Start the function in a new process
                    process = threading.Thread(target=c.playJsonMidiPlay,
                                               args=(clocking, playlist,
                                                         self.loops,
                                                         self.verbose,
                                                         self.talkie_delay_ms))
                    process.start()
                    operand >> Plot(self.block)
                else:
                    if self.plot and not self.block:
                        operand >> Plot(self.block)
                    c.playJsonMidiPlay(clocking, playlist,
                                            self.loops,
                                            self.verbose,
                                            self.talkie_delay_ms)
                return operand
            case od.Line():
                line_clip = oc.Clip(operand)
                self.__rrshift__(line_clip)
            case str():
                line = od.Line(operand)
                self.__rrshift__(line)
            case _:
                return super().__rrshift__(operand)
    
    @staticmethod
    def play(operand: o.T, *parameters) -> o.T:
        return Play(*parameters).__rrshift__(operand)


class Print(Process):
    """`Generic -> Process -> Print`

    Prints the Operand's parameters in a JSON alike layout if it's an `Operand` being given,
    otherwise prints directly like the common `print` function.

    Args:
        formatted (bool): If False prints the `Operand` content in a single line.
    """
    def __init__(self, serialization: bool = False):
        super().__init__()
        self.serialization = serialization

    def process(self, operand: o.T) -> o.T:
        import json
        match operand:
            case oc.Container():
                self.process(operand._items)
            case o.Operand():
                if self.serialization:
                    serialized_json_str = json.dumps(operand.getSerialization())
                    json_object = json.loads(serialized_json_str)
                    json_formatted_str = json.dumps(json_object, indent=4)
                    print(json_formatted_str)
                else:
                    print(operand % str())
            case list():
                print_list = list()
                for value in operand:
                    match value:
                        case o.Operand():
                            print_list.append(value % str())
                        case _:
                            print_list.append(value)
                print(print_list)
            case _:
                print(operand)
        return operand


class Copy(Process):
    """`Generic -> Process -> Copy`

    Creates and returns a copy of the left side `>>` operand.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the copied `Operand`.

    Returns:
        Operand: Returns a copy of the left side `>>` operand.
    """
    def __init__(self, *parameters):
        super().__init__()
        self.parameters = parameters

    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.copy(*self.parameters)
        return o.deep_copy(operand)


class Proxy(Process):
    """`Generic -> Process -> Proxy`

    Creates and returns a shallow copy of the left side `>>` Container.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the shallow copied `Container`.

    Returns:
        Container: Returns a shallow copy of the left side `>>` operand.
    """
    def __init__(self, *parameters):
        super().__init__()
        self.parameters = parameters

    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, oc.Container):
            return operand.shallow_copy(*self.parameters)
        return super().__rrshift__(operand)


class Reset(Process):
    """`Generic -> Process -> Reset`

    Does a reset of the Operand's original parameters and its volatile ones.

    Parameters
    ----------
    Any(None) : The Parameters to be set on the reset `Operand`.

    Returns:
        Operand: Returns the same reset operand.
    """
    def __init__(self, *parameters):
        super().__init__()
        self.parameters = parameters

    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.reset(*self.parameters)
        return super().__rrshift__(operand)


class Clear(Process):
    """`Generic -> Process -> Clear`

    Besides doing a reset of the Operand's slate parameters and its volatile ones,
    sets the default parameters associated with an empty Operand (blank slate).

    Parameters
    ----------
    Any(None) : The Parameters to be set on the cleared `Operand`.

    Returns:
        Operand: Returns the same cleared operand.
    """
    def __init__(self, *parameters):
        super().__init__()
        self.parameters = parameters

    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, o.Operand):
            return operand.clear(*self.parameters)
        return super().__rrshift__(operand)



class Read(Process):
    """`Generic -> Process -> Read`

    Reads the keyboard input. Press and release SHIFT for each Element. Press ENTER to stop.

    Args:
        None
    """
    def process(self, operand: o.T) -> o.T:
        if isinstance(operand, (oe.Element, ou.Tempo)):
            return operand.read()
        else:
            print(f"Warning: Operand is NOT an `Element` or a `Tempo`!")
        return super().__rrshift__(operand)



