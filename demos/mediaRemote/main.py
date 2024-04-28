#demos/mediaRemote: Turn your microcontroller board into a media remote receiver for your PC/Mac.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.Timebase import now_ms, ms_elapsed
from CelIRcom.EasyIRRx import EasyRx
from EasyActuation.USBHID_Keyboard import KeysMain, KeysCC, Keycode, CCC
import board


#=Platform/build-dependent config
#===============================================================================
rx_pin = board.GP16 #RP2040 nano


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
SIGNAL_MAP_ADAFRUIT = {
    0xFF6897: KeysMain(Keycode.KEYPAD_ZERO), #0
    0xFF30CF: KeysMain(Keycode.KEYPAD_ONE), #1
    0xFF18E7: KeysMain(Keycode.KEYPAD_TWO), #2,
    0xFF7A85: KeysMain(Keycode.KEYPAD_THREE), #3,
    0xFF10EF: KeysMain(Keycode.KEYPAD_FOUR), #4,
    0xFF38C7: KeysMain(Keycode.KEYPAD_FIVE), #5,
    0xFF5AA5: KeysMain(Keycode.KEYPAD_SIX), #6,
    0xFF42BD: KeysMain(Keycode.KEYPAD_SEVEN), #7,
    0xFF4AB5: KeysMain(Keycode.KEYPAD_EIGHT), #8,
    0xFF52AD: KeysMain(Keycode.KEYPAD_NINE), #9,
    0xFF22DD: KeysCC(CCC.MUTE), #setup (alternatives: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
    0xFF02FD: KeysMain(Keycode.UP_ARROW), #nav_up
    0xFFE01F: KeysMain(Keycode.LEFT_ARROW), #nav_left
    0xFFA857: KeysMain(Keycode.KEYPAD_ENTER), #nav_enter
    0xFF906F: KeysMain(Keycode.RIGHT_ARROW), #nav_right
    0xFFB04F: KeysMain(Keycode.BACKSPACE), #nav_back
    0xFF9867: KeysMain(Keycode.DOWN_ARROW), #nav_down
    0xFF629D: KeysCC(CCC.PLAY_PAUSE), #play_pause
    0xFFC23D: KeysCC(CCC.STOP), #stop_mode
    0xFFA25D: KeysCC(CCC.VOLUME_DECREMENT), #vol-
    0xFFE21D: KeysCC(CCC.VOLUME_INCREMENT), #vol+
}


#=Event handlers
#===============================================================================
class IRDetect(EasyRx):
    def handle_press(self, msg:IRMsg32):
        key = SIGNAL_MAP_ADAFRUIT.get(msg.bits, None)
        if key is None:
            print("Unknown message:", msg.str_hex())
            return
        print("New message:", msg.str_hex())
        key.press()

    def handle_hold(self, msg:IRMsg32):
        print(f"Repeat!")

    def handle_release(self, msg:IRMsg32):
        key = SIGNAL_MAP_ADAFRUIT.get(msg.bits, None)
        if key is None:
            return
        key.release()

irdetect = IRDetect(rx, PDE.DecoderNEC(), PDE.DecoderNECRPT(), msgRPT=PDE.IRMSG32_NECRPT)


#=State
#===============================================================================
signal_last = None
signal_last_startMS = now_ms()


#=Main loop
#===============================================================================
print("mediaRemote: ready to receive!")
print("\nHI2")
while True:
    irdetect.process_events()
#end program