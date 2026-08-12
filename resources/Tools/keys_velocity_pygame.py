import pygame.midi  # pip install mido pygame
import time

# Initialize MIDI
pygame.midi.init()

# === SELECT PORTS ===
# List all devices
for i in range(pygame.midi.get_count()):
    info = pygame.midi.get_device_info(i)
    interf, name, input_dev, output_dev, opened = info
    print(f"ID {i}: {name.decode()}  Input={input_dev} Output={output_dev}")

# Replace these with the correct IDs from your printout
INPUT_ID = 1   # your keyboard input
OUTPUT_ID = 2  # your loopMIDI output

midi_in = pygame.midi.Input(INPUT_ID)
midi_out = pygame.midi.Output(OUTPUT_ID)

print("Running velocity-mapper. Press Ctrl+C to stop...")

try:
    while True:
        if midi_in.poll():
            events = midi_in.read(10)  # read up to 10 events at once
            for event in events:
                data, timestamp = event
                status, note, velocity, _ = data

                # Only map Note On events
                if status == 144 and velocity > 0:
                    # --- VELOCITY REMAPPING ---
                    # Example: compress low velocities, leave highs near full
                    new_velocity = int(80 + (velocity / 127) * 47)  # range 80-127
                    data = [status, note, new_velocity, 0]
                
                # Forward the message
                midi_out.write_short(*data)

        time.sleep(0.001)  # small delay to prevent 100% CPU

except KeyboardInterrupt:
    print("\nStopping...")

finally:
    midi_in.close()
    midi_out.close()
    pygame.midi.quit()
