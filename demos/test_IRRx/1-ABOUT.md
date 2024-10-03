## `test_IRRx`: A CircuitPython project
Test receiving/decoding/capturing IR signals and their associated HEX representation.

# Features:
- Displays IR codes in HEX, and as a bit sequence.
- Modifiable to use "any" IR remote (supported by `CelIRcom` lib).

# Provided/tested configuration
- Pre-configured for Raspberry Pi Pico RP2040 board.

# Comments
- Should work on any microcontroller supported by the CircuitPython `pulseio` lib (not just RP2040).
- Currently limited to protocols supported by `CelIRcom` lib.