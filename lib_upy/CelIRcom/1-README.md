## `CelIRcom`: ***C***onsumer ***el***ectronics ***IR*** ***com***munications module.

# Conventions used in the codebase
<!----------------------------------------------------------------------------->
- Start bits/stop bits: AKA preamble/postamble.
- Most IR messages are made up of \<start bits\>\<message itself\>\<stop bits\>.
- Protocols should be isolated to their own file (module) so one can more
  easily load only code for the desired protocols.
- Different RX/TX implementations (ex: for different backend libraries) should
  be split out into their own files (modules) so code does not crash if one
  of the (alternate) backend libraries is missing. Also: potentially save space.
- Timing values of signal pulses are in ns - whereas everything else is in ms
  in order to minimize computational/space demands.
- Trying to keep identifiers/variable names shorter. Apparently it matters for
  space/speed?.

# TODO
- Request that `pulseio` register start time of first pulse somehow. This could
  improve robustness of `CelIRcom` code.
