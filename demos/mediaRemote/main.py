#demos/mediaRemote: Turn your microcontroller board into a media remote receiver for your PC/Mac.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.Timebase import now_ms, ms_elapsed
from adafruit_hid.consumer_control_code import ConsumerControlCode as CCC
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import usb_hid
import board


#=Platform/build-dependent config
#===============================================================================
rx_pin = board.GP16 #RP2040 nano


#=Classes
#===============================================================================
class KeySequence: #Common interface for Keyboard
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


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
rx.decoders_setactive([
    PDE.DecoderNEC(), PDE.DecoderNECRPT(),
])
MSG_INTERVALMS = round(PDE.IRProtocols.NEC.msgintervalMS * 1.5) #Pad tolerance on interval (don't ignore repeats due to slight mis-timings)
kbd = Keyboard(usb_hid.devices)
cc = ConsumerControl(usb_hid.devices)
def SeqKBD(signal_or_seq): #Convenience constructor
    return KeySequence(kbd, signal_or_seq)
def SeqCC(signal_or_seq): #Convenience constructor
    return KeySequence(cc, signal_or_seq, release_has_args=False)

SIGNAL_MAP_ADAFRUIT = {
    0xFF6897: SeqKBD(Keycode.KEYPAD_ZERO), #0
    0xFF30CF: SeqKBD(Keycode.KEYPAD_ONE), #1
    0xFF18E7: SeqKBD(Keycode.KEYPAD_TWO), #2,
    0xFF7A85: SeqKBD(Keycode.KEYPAD_THREE), #3,
    0xFF10EF: SeqKBD(Keycode.KEYPAD_FOUR), #4,
    0xFF38C7: SeqKBD(Keycode.KEYPAD_FIVE), #5,
    0xFF5AA5: SeqKBD(Keycode.KEYPAD_SIX), #6,
    0xFF42BD: SeqKBD(Keycode.KEYPAD_SEVEN), #7,
    0xFF4AB5: SeqKBD(Keycode.KEYPAD_EIGHT), #8,
    0xFF52AD: SeqKBD(Keycode.KEYPAD_NINE), #9,
    0xFF22DD: SeqCC(CCC.MUTE), #setup (alternatives: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
    0xFF02FD: SeqKBD(Keycode.UP_ARROW), #nav_up
    0xFFE01F: SeqKBD(Keycode.LEFT_ARROW), #nav_left
    0xFFA857: SeqKBD(Keycode.KEYPAD_ENTER), #nav_enter
    0xFF906F: SeqKBD(Keycode.RIGHT_ARROW), #nav_right
    0xFFB04F: SeqKBD(Keycode.BACKSPACE), #nav_back
    0xFF9867: SeqKBD(Keycode.DOWN_ARROW), #nav_down
    0xFF629D: SeqCC(CCC.PLAY_PAUSE), #play_pause
    0xFFC23D: SeqCC(CCC.STOP), #stop_mode
    0xFFA25D: SeqCC(CCC.VOLUME_DECREMENT), #vol-
    0xFFE21D: SeqCC(CCC.VOLUME_INCREMENT), #vol+
}


#=State
#===============================================================================
signal_last = None
signal_last_startMS = now_ms()


#=Main loop
#===============================================================================
print("mediaRemote: ready to receive!")
print(f"MSG_INTERVALMS = {MSG_INTERVALMS}ms")
print("\nHI0")
while True:
    signal_read_startMS = now_ms() #Proxy for start of message reception
    msg:IRMsg32 = rx.msg_read() #Auto prints message when recieves one
    deltaMS = ms_elapsed(signal_last_startMS, signal_read_startMS)

    msg_new = False #Initialize for current loop iteration
    release = (deltaMS > MSG_INTERVALMS)
    if PDE.IRMSG32_NECRPT == msg:
        print(f"Repeat!")
        signal_last_startMS = signal_read_startMS
    elif msg != None: #...But not repeat
        release = True #HAVE to release previous one... otherwise: will press multiple keys
        msg_new = True

    if release and (signal_last != None):
        print(f"Release! (t={deltaMS}ms)")
        signal_last.release()
        signal_last = None
    if msg_new:
        signal_last_startMS = signal_read_startMS
        signal_last = SIGNAL_MAP_ADAFRUIT.get(msg.bits, None)
        if signal_last is None:
            print("Unknown message:", msg.str_hex())
            continue #Button not assigned to any function
        print("New message:", msg.str_hex())
        signal_last.press()
#end program