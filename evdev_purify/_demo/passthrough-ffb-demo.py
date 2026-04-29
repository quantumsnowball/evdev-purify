# /// script
# dependencies = [
#   "evdev",
# ]
# ///

import threading

import evdev
from evdev import ecodes as es

name = '/dev/input/event256'
real_dev = evdev.InputDevice(name)

virtual_dev = evdev.UInput.from_device(
    real_dev,
    name=f'Passthrough: {name}',
    filtered_types=(es.EV_SYN, ),
)

# caps
print(f'{real_dev.capabilities()=}')
print(f'{virtual_dev.capabilities()=}')

# Keeps track of which effects have been uploaded to the device
effects = set()


def ffb_worker() -> None:
    print('FFB thread started...')
    for event in virtual_dev.read_loop():
        # Handle the special uinput events
        if event.type == es.EV_UINPUT:

            if event.code == es.UI_FF_UPLOAD:
                upload = virtual_dev.begin_upload(event.value)

                # Checks if this is a new effect
                if upload.effect.id not in effects:
                    effects.add(upload.effect.id)
                    # Setting id to 1 indicates that a new effect must be allocated
                    upload.effect.id = -1

                real_dev.upload_effect(upload.effect)
                upload.retval = 0
                virtual_dev.end_upload(upload)

            elif event.code == es.UI_FF_ERASE:
                erase = virtual_dev.begin_erase(event.value)
                erase.retval = 0
                real_dev.erase_effect(erase.effect_id)
                effects.remove(erase.effect_id)
                virtual_dev.end_erase(erase)

        # Forward writes to actual rumble device.
        elif event.type == es.EV_FF:
            real_dev.write(event.type, event.code, event.value)


def event_worker():
    print('Input thread started...')
    # Grab the device so other apps don't see the 'raw' unmapped input
    real_dev.grab()
    try:
        for event in real_dev.read_loop():
            # Apply your remapping logic here
            # Example: if event.code == es.BTN_EAST: ...

            # Forward the event to the virtual device
            virtual_dev.write(event.type, event.code, event.value)
    finally:
        real_dev.ungrab()


if __name__ == '__main__':
    t1 = threading.Thread(target=ffb_worker)
    t2 = threading.Thread(target=event_worker)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
