## `mediaRemote`: A CircuitPython project
Turn your microcontroller board into a media remote receiver for your PC/Mac.

# Features:
- Modifiable to use any IR remote.
- Can send any keys supported by `adafruit_hid` lib (not just media keys).

# Provided/tested configuration
- Configured for Raspberry Pi Pico RP2040 bord.
- Preset to work with Adafruit mini remote control (ID 389).

# Comments
- Not tested on Mac. Probably works (uses USB/HID interfae).
- Should work on any microcontroller supported by the MicroPython `pulseio` lib (not just RP2040).
