from evdev import InputDevice, categorize, ecodes

# Replace event0 with the device corresponding to your keyboard
dev = InputDevice('/dev/input/event1')

for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
        key_event = categorize(event)
        if key_event.keystate == key_event.key_down:
            print("Key pressed: ", key_event.keycode)
        elif key_event.keystate == key_event.key_up:
            print("Key released: ", key_event.keycode)