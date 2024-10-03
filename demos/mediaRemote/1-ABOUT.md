## `mediaRemote`: A CircuitPython project
Turn your microcontroller board into a media remote receiver for your PC/Mac.

# Features:
- Modifiable to use any IR remote.
- Can send any keys supported by `adafruit_hid` lib (not just media keys).

# Provided/tested configuration
- Pre-configured for Raspberry Pi Pico RP2040 board.
- Preset to work with Adafruit mini remote control (ID 389).
- Preset to work with [LG-compatible remote HERE](https://www.amazon.ca/dp/B0BHT5BW41) (Good responsiveness).
- Tested on Windows/Mac/Linux.

# Comments
- Should work on any microcontroller supported by the CircuitPython `pulseio` lib (not just RP2040).

# Resources/Links
- <https://docs.circuitpython.org/projects/hid/en/latest/index.html>
