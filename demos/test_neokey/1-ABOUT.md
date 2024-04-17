## `test_neokey`: A CircuitPython project
Test IR control using NeoKey1x4 as input (using I2C).

Not particularly interesting. NeoKey is slow to communicate through I2C.
Slow I2C communications causes timing difficulties sending out NEC-repeat messages.

# Features:

# Provided/tested configuration
- Configured for Raspberry Pi Pico RP2040 board.

# Comments
- Should work on any microcontroller supported by the CircuitPython `pulseio` lib (not just RP2040).
- Currently limited to protocols supported by `CelIRcom` lib.