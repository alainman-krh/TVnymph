<!-- Reference-style links to make tables & lists more readable -->
[CktPy]: <https://docs.circuitpython.org/en/latest>
[RP2040]: <https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html>
[pulseio]: <https://docs.circuitpython.org/en/latest/shared-bindings/pulseio/index.html>

## TVnymph: A CircuitPython project
<!----------------------------------------------------------------------------->
Quickly reconfigure your TV/AV setup for different purposes.
- Watch satellite TV, listen to "net radio", watch your favorite blu-ray disc, etc.
- You can even power down all your equipment with a single press of a button.

NOTE:
- `TVnymph` is technically a CircuitPython toolset that can be customized to
  control any TV/AV setup (and beyond!).

# Demos
<!----------------------------------------------------------------------------->
Demos can be found here in the [`demos/` subdirectory](demos/):
- [`TVnymph_livingroom1`](demos/TVnymph_livingroom1/1-ABOUT.md): A fully-functional example of a `TVnymph` solution (TV+SAT+BRAY).
- [`TVnymph_livingroom2`](demos/TVnymph_livingroom2/1-ABOUT.md): A fully-functional example of a `TVnymph` solution (TV+AV/RX+BRAY+PC).
- [`MediaRemote`](demos/MediaRemote_RP2040/1-ABOUT.md): Media remote receiver for your PC/MAC/thing supporting keyboard media keys.
- [`PCnymph_IRRxClick`](demos/PCnymph_IRRxClick/1-ABOUT.md): Turn your favorite IR remote into a macro pad for Windows.
- [`test_IRTx_neokey`](demos/test_IRTx_neokey/1-ABOUT.md): Test IRTx control using NeoKey1x4 as input.
- [`test_IRRx`](demos/test_IRRx/1-ABOUT.md): Test receiving/decoding IR signals.

# How-To
<!----------------------------------------------------------------------------->
1. [Install](docs/Install.md)
1. [Finding IR-remote codes](docs/FindIRCodes.md)

<!----------------------------------------------------------------------------->
# [Known Issues/TODO](docs/KnownIssues.md)
<!----------------------------------------------------------------------------->

# Compatibility
<!----------------------------------------------------------------------------->
Circuit python platforms supporting the [`pulseio` library][pulseio]
(Expand section labelled ***"Available on these boards"***).

Tested HW+SW platforms/combinations:
- [RP2040] + [CktPy]-9.0.0

