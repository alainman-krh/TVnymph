# `PCnymph_IR2serial`
Turn your favorite IR remote into a macro pad for Windows.

Convert a small RP2040 microcontroller board into an IR signal plug-in
for the PCnymph program (see AVglue project).

TODO: Make PCnymph program. Currently called `samples/mediacontrol_applet`.
Not clear how things connect together.

How?
- Program captures IR signals, and relays a "IR 0xHEXCODE" signal compatible


NOTE:
- Pre-configured for NEC remotes.
- Can re-configure for any protocol supported by CelIRcom module
- Likely supports other microcontrollers (not just RP2040)
