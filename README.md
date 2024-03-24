<!-- Reference-style links to make tables & lists more readable -->
[CktPy]: <https://docs.circuitpython.org/en/latest>
[RP2040]: <https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html>

## TVnymph
<!----------------------------------------------------------------------------->
Quickly reconfigures TV/AV setup for different purposes (satellite TV, net radio, etc).

NOTE:
- `TVnymph` is actually a CircuitPython toolset that can be customized for any
  TV/AV setup (and beyond!).

# Demos
<!----------------------------------------------------------------------------->
Demos can be found here in the [`demos/` subdirectory](demos/):
- `test_neokey`: Test IR control using NeoKey1x4 as input.

# How-To
<!----------------------------------------------------------------------------->
1. [Install](docs/Install.md)


# TODO
<!----------------------------------------------------------------------------->
- Break out `CelIRcom` and `EasyActuation` into their own repositories.
- Figure out how to link them in as submodules.

# Compatibility
<!----------------------------------------------------------------------------->
Circuit python platforms supporting the [`pulseio` library](https://docs.circuitpython.org/en/latest/shared-bindings/pulseio/index.html)
(Expand section labelled ***"Available on these boards"***).

Tested HW+SW platforms/combinations:
- [RP2040] + [CktPy]-8.2.9

