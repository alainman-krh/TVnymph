#EasyActuation/USBHID_Keyboard.py
#-------------------------------------------------------------------------------
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode as CCC #Convenience for module user
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode #Convenience for module user
import usb_hid


#=Constants
#===============================================================================
#Access to standard HID/Keyboard & HID/ConsumerControl
kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)


#=Classes
#===============================================================================
class KeySequence: #Simplified, common interface for HID/Keyboard & HID/ConsumerControl
    def __init__(self, dev, signal_or_seq, release_has_args=True) -> None:
        self.dev = dev
        if type(signal_or_seq) is int:
            signal_or_seq = (signal_or_seq,) #Make tuple
        self.signal_or_seq = signal_or_seq

        signal_or_seq_release = signal_or_seq
        if not release_has_args:
            signal_or_seq_release = tuple() #No args
        self.signal_or_seq_release = signal_or_seq_release
    def press(self):
        self.dev.press(*self.signal_or_seq)
    def release(self):
        self.dev.release(*self.signal_or_seq_release)


#=Convenience/constructor functions
#===============================================================================
def SeqKBD(signal_or_seq):
    return KeySequence(kbd, signal_or_seq)
def SeqCC(signal_or_seq):
    return KeySequence(cc, signal_or_seq, release_has_args=False)

#Last line