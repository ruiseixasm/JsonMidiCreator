import mido # pip install mido python-rtmidi

print("Input ports:", mido.get_input_names())
print("Output ports:", mido.get_output_names())

