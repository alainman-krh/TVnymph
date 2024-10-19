#demos\MediaRemote_RP2040: Media remote receiver for your PC/MAC/thing supporting keyboard media keys.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.EasyIRRx import EasyRx
from EasyCktIO.USBHID_Keyboard import KeysMain, KeysCC, Keycode, CCC
import board


#=Resources for Keycode/CCC (aliases for Keycode/ConsumerControlCode)
#===============================================================================
#https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit-hid-keycode-keycode
#https://docs.circuitpython.org/projects/hid/en/latest/api.html#adafruit_hid.consumer_control_code.ConsumerControlCode


#=Option slect
#===============================================================================
SEND_CONSUMERCONTROL_ONLY = False #Support basic media keys only (remote will not "type text")
USE_NUMPAD = False #Send numpad keys vs standard numbers/enter key (SEND_CONSUMERCONTROL_ONLY must =False)


#=Platform/build-dependent config (Raspberry Pi Pico RP2040)
#===============================================================================
rx_pin = board.GP28
#Not likely to want "extras" to be sent to your PC (numeric values + arrows):


#=Options: Numeric input (+enter/select/ok)
#===============================================================================
KEYMAP_NUMPAD = {
    "1": KeysMain(Keycode.KEYPAD_ONE),   "2": KeysMain(Keycode.KEYPAD_TWO),   "3": KeysMain(Keycode.KEYPAD_THREE),
    "4": KeysMain(Keycode.KEYPAD_FOUR),  "5": KeysMain(Keycode.KEYPAD_FIVE),  "6": KeysMain(Keycode.KEYPAD_SIX),
    "7": KeysMain(Keycode.KEYPAD_SEVEN), "8": KeysMain(Keycode.KEYPAD_EIGHT), "9": KeysMain(Keycode.KEYPAD_NINE),
    "0": KeysMain(Keycode.KEYPAD_ZERO), "SELECT": KeysMain(Keycode.KEYPAD_ENTER),
}
KEYMAP_STD = { #Standard keyboard keys (not numpad)
    "1": KeysMain(Keycode.ONE),   "2": KeysMain(Keycode.TWO),   "3": KeysMain(Keycode.THREE),
    "4": KeysMain(Keycode.FOUR),  "5": KeysMain(Keycode.FIVE),  "6": KeysMain(Keycode.SIX),
    "7": KeysMain(Keycode.SEVEN), "8": KeysMain(Keycode.EIGHT), "9": KeysMain(Keycode.NINE),
    "0": KeysMain(Keycode.ZERO), "SELECT": KeysMain(Keycode.ENTER),
}
KEYMAP = KEYMAP_NUMPAD if USE_NUMPAD else KEYMAP_STD


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
SIGNAL_MAP_ADAFRUIT_389_CCC = { #Mapping for Adafruit 389 Mini Remote Control
    0xFF629D: KeysCC(CCC.PLAY_PAUSE), 0xFFC23D: KeysCC(CCC.STOP),
    0xFFA25D: KeysCC(CCC.VOLUME_DECREMENT), 0xFFE21D: KeysCC(CCC.VOLUME_INCREMENT),
    0xFF22DD: KeysCC(CCC.MUTE), #"setup" button (options: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}
SIGNAL_MAP_ADAFRUIT_389_EXTRAS = { #Extras (numeric + arrows)
    0xFF30CF: KEYMAP["1"], 0xFF18E7: KEYMAP["2"], 0xFF7A85: KEYMAP["3"],
    0xFF10EF: KEYMAP["4"], 0xFF38C7: KEYMAP["5"], 0xFF5AA5: KEYMAP["6"],
    0xFF42BD: KEYMAP["7"], 0xFF4AB5: KEYMAP["8"], 0xFF52AD: KEYMAP["9"],
    0xFF6897: KEYMAP["0"], 0xFFA857: KEYMAP["SELECT"],
    0xFF02FD: KeysMain(Keycode.UP_ARROW), 0xFF9867: KeysMain(Keycode.DOWN_ARROW),
    0xFFE01F: KeysMain(Keycode.LEFT_ARROW), 0xFF906F: KeysMain(Keycode.RIGHT_ARROW),
    0xFFB04F: KeysMain(Keycode.BACKSPACE), #"return"
}

SIGNAL_MAP_LG_CCC = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF0DF2: KeysCC(CCC.PLAY_PAUSE), 0x20DF5DA2: KeysCC(CCC.PLAY_PAUSE), #"play" & "pause" buttons
    0x20DF8D72: KeysCC(CCC.STOP),
    0x20DFF10E: KeysCC(CCC.SCAN_PREVIOUS_TRACK), 0x20DF718E: KeysCC(CCC.SCAN_NEXT_TRACK),
    0x20DFC03F: KeysCC(CCC.VOLUME_DECREMENT), 0x20DF40BF: KeysCC(CCC.VOLUME_INCREMENT),
    0x20DF906F: KeysCC(CCC.MUTE),
}
#Not likely to want "extras" to be sent to your PC:
SIGNAL_MAP_LG_EXTRAS = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF8877: KEYMAP["1"], 0x20DF48B7: KEYMAP["2"], 0x20DFC837: KEYMAP["3"],
    0x20DF28D7: KEYMAP["4"], 0x20DFA857: KEYMAP["5"], 0x20DF6897: KEYMAP["6"],
    0x20DFE817: KEYMAP["7"], 0x20DF18E7: KEYMAP["8"], 0x20DF9867: KEYMAP["9"],
    0x20DF08F7: KEYMAP["0"], 0x20DF22DD: KEYMAP["SELECT"],
    0x20DF02FD: KeysMain(Keycode.UP_ARROW), 0x20DF827D: KeysMain(Keycode.DOWN_ARROW),
    0x20DFE01F: KeysMain(Keycode.LEFT_ARROW), 0x20DF609F: KeysMain(Keycode.RIGHT_ARROW),
    0x20DF14EB: KeysMain(Keycode.BACKSPACE), 0x20DFDA25: KeysMain(Keycode.ESCAPE), #"back" & "exit"
}

#Respond to both remotes (NOTE: cannot have overlapping codes)
SIGNAL_MAP = {}
SIGNAL_MAP.update(SIGNAL_MAP_ADAFRUIT_389_CCC)
SIGNAL_MAP.update(SIGNAL_MAP_LG_CCC)
if not SEND_CONSUMERCONTROL_ONLY:
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