## `CelIRcom`: ***C***onsumer ***el***ectronics ***IR*** ***com***munications module.

# Naming conventions
<!----------------------------------------------------------------------------->
- Preamble/postamble: AKA start bits/stop bits (though not really bits).
- Mark/space (typ. High/Low): Sometimes "mark" is called "pulse.
  - Note: some recievers have inverted logic where "mark" is low, and "space"
    is high.
- A symbol represents either a bit (0 or 1)... or a pair of bits
  (00, 01, 10, 11) in some encoding schemes.
  - Philps RC-MM protocol is an example that uses a Pulse Distance Encoding
    scheme where each symbol represents 2 bits.
- Code refers to an individual "pulse" as a continuous series of ***either***
  "marks" or "spaces" - as opposed to the definition used in signal analysis
  (where a "pulse" is a signal that "pulses" low->high->low).


# Coding conventions
<!----------------------------------------------------------------------------->
- Most IR messages are made up of \<start bits\>\<message itself\>\<stop bits\>.
- Protocols TYPES (ex: Pulse Distance Encoding/Manchester Encoding/...) should
  be isolated to their own file (module) so one can selectively load code for
  ***only*** the desired protocols.
- Different RX/TX implementations (ex: for different backend libraries) should
  be split out into their own files (modules) so code does not crash if one
  of the (alternate) backend libraries is missing. Also: potentially save space.
- THOUGHT: Maybe have a folder for each backend where individual protocol
  implentation is in its own file.
- Timing values of signal pulses are in ns - whereas everything else is in ms
  in order to minimize computational/space demands.
- Trying to keep identifiers/variable names shorter. Apparently it matters for
  space/speed?.


# IR encoding types
<!----------------------------------------------------------------------------->
Listing what I find here... Not sure if names/aliases are correct, though.
- ***Pulse-Distance Encoding (PDE)***: "pulse" width is the same for all
  symbols, and trailing "space" width depends on the symbol being transmitted.
  - AKA: "space encoding".
- ***Pulse-Length Encoding (PLE)***: "pulse" width depends on symbol being
  transmitted, and trailing "space" is of fixed width.
  - AKA: "pulse encoding", "pulse-width encoding", "pulse-duration encoding".
- ***Bi-Phase Encoding (BPE)***: Both symbols (representing either a 0 or 1 bit)
  have fixed widths, but with opposite polarities. For example: A "mark-space"
  pattern represents a 0 bit, whereas a "space-mark" pattern represents a 1 bit
  (or vice-versa).
  - AKA: "Manchester encoding"

Good overview of encoding types:
- <https://techdocs.altium.com/display/FPGA/Infrared+Communication+Concepts>

# TODO
<!----------------------------------------------------------------------------->
- Request that `pulseio` register start time of first pulse somehow. This could
  improve robustness of `CelIRcom` code.
