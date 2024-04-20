## TVnymph: Finding IR-remote codes
<!----------------------------------------------------------------------------->
The easiest way to find IR-remote codes for your device is to capture them
directly from the original remote. You can use one of the following (included)
CircuitPython programs to capture IR-remotes codes:
- [`PCnymph_IRRxClick`](../demos/PCnymph_IRRxClick/1-ABOUT.md): Very terse output.
- [`test_IRRx`](../demos/test_IRRx/1-ABOUT.md): Verbose output (also displays un-recognized signals).

Both print out detected IR signals on CircuitPython's serial output.

# What about direct-input select and direct power on/off?
<!----------------------------------------------------------------------------->
Typical IR-remotes supplied with TVs/AV equipment come with a somewhat
inconvenient "cycling" input select button, and "toggling" power buttons. These
buttons are not very practical for getting `TVnymph` to perform its magic.

Ideally, you should use the DIRECT \{power-on, power-off, and input select\}
commands with `TVnymph`. Unfortunately, these can be a bit tough to find.

## DIRECT input/power controls: Logitech Harmony remote
One effective solution to finding specific IR codes is to first program a
Logitech Harmony remote to control the device of interest. Note that not all
Harmony remotes have the same capabilities.

One remote that has been successfully used to find the direct-input select
and direct power on/off buttons is the Harmony 650. Like many remotes, the
Harmony 650 remote has a wide array of common buttons directly accesible on its
face.
- Note that these face buttons typically will not send direct-input or direct power on/off buttons.
- However, the Harmony software DO provide access to the direct-input and direct
  power on/off messages from its special LCD menu system.

Sadly, Logitech has discontinued the Harmony series of remotes. Getting access
to such a device will likely be a somewhat challenging endeavor.

## DIRECT input/power controls: Online resources
Another way to find the direct input & power controls is to search online.
I have not personally had much success with this approch, but I will list some
of the resources I have found here:
- <https://lirc.sourceforge.net/remotes/>
- <http://www.hifi-remote.com/sony/>

## DIRECT input/power controls: Included in this project
This project comes bundled ([here](../codes_irremotes/)) with select IR codes
needed to control a few devices. The list of included devices is by no means
exhaustive... but who knows?... Maybe you will find a device with compatible
IR codes.
