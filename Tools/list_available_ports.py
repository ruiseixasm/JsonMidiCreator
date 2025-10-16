import rtmidi

midi_in = rtmidi.MidiIn()
midi_out = rtmidi.MidiOut()

print("Input ports:", midi_in.get_ports())
print("Output ports:", midi_out.get_ports())
