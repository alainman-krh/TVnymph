# `PCnymph_IRRxClick`: A CircuitPython project
Turn your favorite IR remote into a macro pad for Windows.

# Details
Converts your favorite microcontroller board into a click-in
IR reciever module for the `PCnymph` program (see `AVglue` project).

How?
- This CircuitPython program captures IR signals, and supplies an
  "IR\[PROTOCOL\] 0xHEXCODE" signal compatible with the `PCnymph`
  python/Windows program.

# Provided/tested configuration
- Forwards received IR controller signals through your microcontroller's
  serial-over-USB connection.
- Pre-configured for Raspberry Pi Pico RP2040 board.
- Pre-configured to detect standard NEC consumer IR-remote signals.

# Comments
- Should work on any microcontroller supported by the CircuitPython `pulseio` lib (not just RP2040).
- Can re-configure to recieve any protocol supported by `CelIRcom` lib.

# TODO
- Make `PCnymph` program (Currently called `samples/mediacontrol_applet`).
- Make it clear for user how things connect together.
