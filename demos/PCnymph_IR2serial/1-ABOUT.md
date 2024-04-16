# `PCnymph_IR2serial`: A CircuitPython project
Turn your favorite IR remote into a macro pad for Windows.

# Details
Converts your favorite microcontroller board into an IR reciever module
that connects/talks to the `PCnymph` program (see AVglue project).

How?
- Program captures IR signals, and relays a "IR\[PROTOCOL\] 0xHEXCODE"
  signal compatible with the `PCnymph` program.

# Provided/tested configuration
- Configured for Raspberry Pi Pico RP2040 board.
- Preset to relay any standard NEC IR controller signals through the
  serial connection on your microcontroller's USB port.

# TODO
- Make `PCnymph` program.
- Currently called `samples/mediacontrol_applet`.
- Not clear for user how things connect together.

NOTE:
- Pre-configured for NEC remotes.
- Can re-configure for any protocol supported by `CelIRcom` lib.
- Should work on any microcontroller supported by the MicroPython `pulseio` lib (not just RP2040).