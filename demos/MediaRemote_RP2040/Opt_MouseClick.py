#MediaRemote_RP2040\Opt_MouseClick.py: Optionally handle some buttons as mouse clicks.
#-------------------------------------------------------------------------------
from CelIRcom.ProtocolsBase import IRMsg32
from adafruit_hid.mouse import Mouse
import usb_hid

mouse = Mouse(usb_hid.devices)

def handle_mouseclick(msg:IRMsg32):
	if (0x20DF4EB1 == msg.bits): #LG red button
		mouse.click(Mouse.LEFT_BUTTON)
	else:
		return False #Indicate that nothing was detected
	return True