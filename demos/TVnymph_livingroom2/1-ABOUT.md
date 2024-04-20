## `TVnymph_livingroom2`: A CircuitPython project
Quickly reconfigure your TV/AV setup (TV+AV/RX+BRAY+PC) for different purposes.

# Features:
- Modifiable to use "any" IR remote/AV setup (supported by `CelIRcom` lib).

# Provided/tested configuration
- Configured for Raspberry Pi Pico RP2040 board.

# Comments
- Should work on any microcontroller supported by the CircuitPython `pulseio` lib (not just RP2040).
- Currently limited to protocols supported by `CelIRcom` lib.
- IR codes can be captured using the [`demos/test_IRRx`](../test_IRRx/1-ABOUT.md) program.