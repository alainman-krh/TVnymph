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
SEND_SKIP_IF_FFREW_ONLY = True #Send "skip" keys on remotes that only support FF/RW (no proper skip buttons)
SEND_NUMPAD = True #Send numpad keys vs standard numbers/enter key (SEND_CONSUMERCONTROL_ONLY must =False)


#=Platform/build-dependent config (Raspberry Pi Pico RP2040)
#===============================================================================
rx_pin = board.GP28
#Not likely to want "extras" to be sent to your PC (numeric values + arrows):


#=Base keymap
#===============================================================================
FRAME_FORWARD = 0xC6
KEYMAP = {
    "PLAY": KeysCC(CCC.PLAY_PAUSE)        , "PAUSE": KeysCC(CCC.PLAY_PAUSE),
    "STOP": KeysCC(CCC.STOP)              , "EJECT": KeysCC(CCC.EJECT),
    "<<" : KeysCC(CCC.REWIND)             , ">>" :   KeysCC(CCC.FAST_FORWARD),
    "|<<": KeysCC(CCC.SCAN_PREVIOUS_TRACK), ">>|":   KeysCC(CCC.SCAN_NEXT_TRACK),
    "VOL-": KeysCC(CCC.VOLUME_DECREMENT)  , "VOL+":  KeysCC(CCC.VOLUME_INCREMENT),
    "MUTE": KeysCC(CCC.MUTE),

    "1": KeysMain(Keycode.ONE),   "2": KeysMain(Keycode.TWO),   "3": KeysMain(Keycode.THREE),
    "4": KeysMain(Keycode.FOUR),  "5": KeysMain(Keycode.FIVE),  "6": KeysMain(Keycode.SIX),
    "7": KeysMain(Keycode.SEVEN), "8": KeysMain(Keycode.EIGHT), "9": KeysMain(Keycode.NINE),
    "0": KeysMain(Keycode.ZERO) , "SELECT": KeysMain(Keycode.ENTER),

    "NAV_UP":   KeysMain(Keycode.UP_ARROW)  , "NAV_DOWN":  KeysMain(Keycode.DOWN_ARROW),
    "NAV_LEFT": KeysMain(Keycode.LEFT_ARROW), "NAV_RIGHT": KeysMain(Keycode.RIGHT_ARROW),
    "BACK":     KeysMain(Keycode.BACKSPACE) , "EXIT":      KeysMain(Keycode.ESCAPE),
}

#=Options: Numeric input (+enter/select/ok)
#===============================================================================
KEYMAP_NUMPAD = {
    "1": KeysMain(Keycode.KEYPAD_ONE),   "2": KeysMain(Keycode.KEYPAD_TWO),   "3": KeysMain(Keycode.KEYPAD_THREE),
    "4": KeysMain(Keycode.KEYPAD_FOUR),  "5": KeysMain(Keycode.KEYPAD_FIVE),  "6": KeysMain(Keycode.KEYPAD_SIX),
    "7": KeysMain(Keycode.KEYPAD_SEVEN), "8": KeysMain(Keycode.KEYPAD_EIGHT), "9": KeysMain(Keycode.KEYPAD_NINE),
    "0": KeysMain(Keycode.KEYPAD_ZERO) , "SELECT": KeysMain(Keycode.KEYPAD_ENTER),
}
if SEND_NUMPAD:
    KEYMAP.update(KEYMAP_NUMPAD) #Overwrite with numpad characters


#=Options: FF/REW and skip buttons
#===============================================================================
#Special option for remotes supporting ONLY FF/REW (not next/previous track):
SKIPCHAR = "|" if SEND_SKIP_IF_FFREW_ONLY else "" #Switch to "skip" keys if requested
KEYMAP_FRONLY = {
    "<<" : (KEYMAP[SKIPCHAR+"<<"]),
    ">>" : (KEYMAP[">>"+SKIPCHAR]),
}


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
SIGNAL_MAP_ADAFRUIT_389_CCC = { #Mapping for Adafruit 389 Mini Remote Control
    0xFF629D: KEYMAP["PLAY"], 0xFFC23D: KEYMAP["STOP"],
    0xFFA25D: KEYMAP["VOL-"], 0xFFE21D: KEYMAP["VOL+"],
    0xFF22DD: KEYMAP["MUTE"], #"setup" button (options: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}
SIGNAL_MAP_ADAFRUIT_389_EXTRAS = { #Extras (numeric + arrows)
    0xFF30CF: KEYMAP["1"], 0xFF18E7: KEYMAP["2"], 0xFF7A85: KEYMAP["3"],
    0xFF10EF: KEYMAP["4"], 0xFF38C7: KEYMAP["5"], 0xFF5AA5: KEYMAP["6"],
    0xFF42BD: KEYMAP["7"], 0xFF4AB5: KEYMAP["8"], 0xFF52AD: KEYMAP["9"],
    0xFF6897: KEYMAP["0"], 0xFFA857: KEYMAP["SELECT"],
    0xFF02FD: KEYMAP["NAV_UP"], 0xFF9867: KEYMAP["NAV_DOWN"],
    0xFFE01F: KEYMAP["NAV_LEFT"], 0xFF906F: KEYMAP["NAV_RIGHT"],
    0xFFB04F: KEYMAP["EXIT"], #"return"
}

SIGNAL_MAP_LG_CCC = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF0DF2: KEYMAP["PLAY"], 0x20DF5DA2: KEYMAP["PAUSE"], 0x20DF8D72: KEYMAP["STOP"],
    0x20DFF10E: KEYMAP_FRONLY["<<"], 0x20DF718E: KEYMAP_FRONLY[">>"],
    0x20DFC03F: KEYMAP["VOL-"], 0x20DF40BF: KEYMAP["VOL+"],
    0x20DF906F: KEYMAP["MUTE"],
}
#Not likely to want "extras" to be sent to your PC:
SIGNAL_MAP_LG_EXTRAS = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF8877: KEYMAP["1"], 0x20DF48B7: KEYMAP["2"], 0x20DFC837: KEYMAP["3"],
    0x20DF28D7: KEYMAP["4"], 0x20DFA857: KEYMAP["5"], 0x20DF6897: KEYMAP["6"],
    0x20DFE817: KEYMAP["7"], 0x20DF18E7: KEYMAP["8"], 0x20DF9867: KEYMAP["9"],
    0x20DF08F7: KEYMAP["0"], 0x20DF22DD: KEYMAP["SELECT"],
    0x20DF02FD: KEYMAP["NAV_UP"], 0x20DF827D: KEYMAP["NAV_DOWN"],
    0x20DFE01F: KEYMAP["NAV_LEFT"], 0x20DF609F: KEYMAP["NAV_RIGHT"],
    0x20DF14EB: KEYMAP["BACK"], 0x20DFDA25: KEYMAP["EXIT"],
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