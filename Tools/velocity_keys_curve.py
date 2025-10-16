import rtmidi   # Run `python -m pip install python-rtmidi`

# Initialize MIDI input and output
midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()

# List available ports
print("Available input ports:", midi_in.get_ports())
print("Available output ports:", midi_out.get_ports())

# Open your keyboard input and virtual output
midi_in.open_port(0)     # your keyboard
midi_out.open_port(1)    # your virtual port (loopMIDI/IAC)

print("Running... Press Ctrl+C to stop.")

while True:
    msg = midi_in.get_message()
    if msg:
        message, delta = msg
        # MIDI Note On event
        if message[0] & 0xF0 == 0x90 and message[2] > 0:
            note = message[1]
            velocity = 127  # or remap e.g. int(message[2]*1.5)
            midi_out.send_message([0x90, note, min(127, velocity)])
        else:
            # Forward other messages as-is
            midi_out.send_message(message)
