#demos\MediaRemote_RP2040: Turn your microcontroller board into a media remote receiver for your PC/Mac.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.Timebase import now_ms, ms_elapsed
from CelIRcom.EasyIRRx import EasyRx
from EasyCktIO.USBHID_Keyboard import KeysMain, KeysCC, Keycode, CCC
import board


#=Resources for Keycode/CCC (aliases for Keycode/ConsumerControlCode)
#===============================================================================
#https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
#https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode


#=Platform/build-dependent config (Raspberry Pi Pico RP2040)
#===============================================================================
rx_pin = board.GP16
#Not likely to want "extras" to be sent to your PC (numeric values + arrows):
USE_EXTRAS = False


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
SIGNAL_MAP_ADAFRUIT_389 = { #Mapping for Adafruit 389 Mini Remote Control
    0xFF629D: KeysCC(CCC.PLAY_PAUSE), #play_pause
    0xFFC23D: KeysCC(CCC.STOP), #stop_mode
    0xFFA25D: KeysCC(CCC.VOLUME_DECREMENT), #vol-
    0xFFE21D: KeysCC(CCC.VOLUME_INCREMENT), #vol+
    0xFF22DD: KeysCC(CCC.MUTE), #setup (alternatives: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}
SIGNAL_MAP_ADAFRUIT_389_EXTRAS = { #Extras (numeric + arrows)
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
    0xFF22DD: KeysCC(CCC.MUTE), #setup (alternatives: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}

SIGNAL_MAP_LG = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF0DF2: KeysCC(CCC.PLAY_PAUSE), #play_pause
    0x20DF5DA2: KeysCC(CCC.PLAY_PAUSE), #play_pause
    0x20DFF10E: KeysCC(CCC.SCAN_PREVIOUS_TRACK),
    0x20DF718E: KeysCC(CCC.SCAN_NEXT_TRACK),
    0x20DF8D72: KeysCC(CCC.STOP), #stop_mode
    0x20DFC03F: KeysCC(CCC.VOLUME_DECREMENT), #vol-
    0x20DF40BF: KeysCC(CCC.VOLUME_INCREMENT), #vol+
    0x20DF906F: KeysCC(CCC.MUTE), #setup (alternatives: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}
#Not likely to want "extras" to be sent to your PC:
SIGNAL_MAP_LG_EXTRAS = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF08F7: KeysMain(Keycode.KEYPAD_ZERO), #0
    0x20DF8877: KeysMain(Keycode.KEYPAD_ONE), #1
    0x20DF48B7: KeysMain(Keycode.KEYPAD_TWO), #2,
    0x20DFC837: KeysMain(Keycode.KEYPAD_THREE), #3,
    0x20DF28D7: KeysMain(Keycode.KEYPAD_FOUR), #4,
    0x20DFA857: KeysMain(Keycode.KEYPAD_FIVE), #5,
    0x20DF6897: KeysMain(Keycode.KEYPAD_SIX), #6,
    0x20DFE817: KeysMain(Keycode.KEYPAD_SEVEN), #7,
    0x20DF18E7: KeysMain(Keycode.KEYPAD_EIGHT), #8,
    0x20DF9867: KeysMain(Keycode.KEYPAD_NINE), #9,
    0x20DF02FD: KeysMain(Keycode.UP_ARROW), #nav_up
    0x20DFE01F: KeysMain(Keycode.LEFT_ARROW), #nav_left
    0x20DF22DD: KeysMain(Keycode.KEYPAD_ENTER), #nav_enter
    0x20DF609F: KeysMain(Keycode.RIGHT_ARROW), #nav_right
    0x20DF14EB: KeysMain(Keycode.BACKSPACE), #nav_back
    0x20DF827D: KeysMain(Keycode.DOWN_ARROW), #nav_down
    0x20DFDA25: KeysMain(Keycode.ESCAPE),
}

#Respond to both remotes (NOTE: cannot have overlapping codes)
SIGNAL_MAP = {}
SIGNAL_MAP.update(SIGNAL_MAP_ADAFRUIT_389)
SIGNAL_MAP.update(SIGNAL_MAP_LG)
if USE_EXTRAS:
    SIGNAL_MAP.update(SIGNAL_MAP_ADAFRUIT_389_EXTRAS)
    SIGNAL_MAP.update(SIGNAL_MAP_LG_EXTRAS)


#=Event handlers
#===============================================================================
class IRDetect(EasyRx):
    def handle_press(self, msg:IRMsg32):
        key = SIGNAL_MAP.get(msg.bits, None)
        if key is None:
            print("Unknown message:", msg.str_hex())
            return
        print("New message:", msg.str_hex())
        key.press()

    def handle_hold(self, msg:IRMsg32):
        print(f"Repeat!")

    def handle_release(self, msg:IRMsg32):
        key = SIGNAL_MAP.get(msg.bits, None)
        if key is None:
            return
        key.release()

irdetect = IRDetect(rx, PDE.DecoderNEC(), PDE.DecoderNECRPT(), msgRPT=PDE.IRMSG32_NECRPT)


#=Main loop
#===============================================================================
print("HELLO24") #DEBUG: Change me to ensure uploaded version matches.
print("MediaRemote: ready to receive!")
while True:
    irdetect.process_events()
#end program