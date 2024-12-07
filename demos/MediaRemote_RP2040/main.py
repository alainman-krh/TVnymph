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


#=Option select
#===============================================================================
SEND_CONSUMERCONTROL_ONLY = False #Support basic media keys only (remote will not "type text")
#==> (Not likely to want "extras" to be sent to your PC (numeric values + arrows))
SEND_SKIP_IF_FFREW_ONLY = True #Send "skip" keys on remotes that only support FF/RW (no proper skip buttons)
SEND_NUMPAD = True #Send numpad keys vs standard numbers/enter key (SEND_CONSUMERCONTROL_ONLY must =False)
USEOPT_MOUSECLICK = True #Use optional mouse click

if USEOPT_MOUSECLICK:
	from Opt_MouseClick import handle_mouseclick
	print("Mouse click option enabled")


#=Platform/build-dependent config
#===============================================================================
#Choose pin used for receiving IR signals (depends on platform/variant):
if board.board_id in ("raspberry_pi_pico", "raspberry_pi_pico2"):
    rx_pin = board.GP28 #Default to use (for standard RP2040-Pico board)
    #rx_pin = board.GP3 #Variant: RP2040-Pico with custom protoboard
    #rx_pin = board.GP4 #Variant: RP2040-Pico on PiCowbell STEMMA-QT port (Signal: SDA)
elif "adafruit_kb2040" == board.board_id:
    rx_pin = board.D9 #KB2040 "Kee Boar" variant/build using pin on opposite end from USB
elif "adafruit_qt2040_trinkey" == board.board_id:
    rx_pin = board.SDA #Only the STEMMA-QT port is available.
elif "circuitplayground_express" == board.board_id:
    #Doesn't work: Runs out of memory
    rx_pin = board.REMOTEIN #Adafruit Circuit Playground Express (built-in IR receiver)
elif "circuitplayground_bluefruit" == board.board_id:
    rx_pin = board.SDA #Adafruit Circuit Playground Bluefruit
else: #No specific variant/build defined. Default to using SDA port
    rx_pin = board.SDA #Typically on the BUILT-IN STEMMA-QT port (for Adafruit boards)


#=Base keymap (Maps the function of a button to corresponding keyboard keys)
#===============================================================================
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
KEYMAP["<<-only"] = KEYMAP[SKIPCHAR+"<<"]
KEYMAP[">>-only"] = KEYMAP[">>"+SKIPCHAR]


#=Signal map: Maps IR remote signals to the function associated with the button
#===============================================================================
SIGNAL_MAP_ADAFRUIT_389_CCC = { #Mapping for Adafruit 389 Mini Remote Control
    0xFF629D: "PLAY", 0xFFC23D: "STOP",
    0xFFA25D: "VOL-", 0xFFE21D: "VOL+",
    0xFF22DD: "MUTE", #"setup" button (options: ESCAPE, KEYPAD_NUMLOCK, MUTE?)
}
SIGNAL_MAP_ADAFRUIT_389_EXTRAS = { #Extras (numeric + arrows)
    0xFF30CF: "1", 0xFF18E7: "2", 0xFF7A85: "3",
    0xFF10EF: "4", 0xFF38C7: "5", 0xFF5AA5: "6",
    0xFF42BD: "7", 0xFF4AB5: "8", 0xFF52AD: "9",
    0xFF6897: "0", 0xFFA857: "SELECT",
    0xFF02FD: "NAV_UP", 0xFF9867: "NAV_DOWN",
    0xFFE01F: "NAV_LEFT", 0xFF906F: "NAV_RIGHT",
    0xFFB04F: "EXIT", #"return"
}

SIGNAL_MAP_LG_CCC = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF0DF2: "PLAY", 0x20DF5DA2: "PAUSE", 0x20DF8D72: "STOP",
    0x20DFF10E: "<<-only", 0x20DF718E: ">>-only",
    0x20DFC03F: "VOL-", 0x20DF40BF: "VOL+",
    0x20DF906F: "MUTE",
}
#Not likely to want "extras" to be sent to your PC:
SIGNAL_MAP_LG_EXTRAS = { #Mapping for some LG IR remote (NEC protocol)
    0x20DF8877: "1", 0x20DF48B7: "2", 0x20DFC837: "3",
    0x20DF28D7: "4", 0x20DFA857: "5", 0x20DF6897: "6",
    0x20DFE817: "7", 0x20DF18E7: "8", 0x20DF9867: "9",
    0x20DF08F7: "0", 0x20DF22DD: "SELECT",
    0x20DF02FD: "NAV_UP", 0x20DF827D: "NAV_DOWN",
    0x20DFE01F: "NAV_LEFT", 0x20DF609F: "NAV_RIGHT",
    0x20DF14EB: "BACK", 0x20DFDA25: "EXIT",
}
SIGNAL_MAP_SAMSUNG_EXAMPLE = { #Mapping for some Samsung IR remote
    0xE0E0D02F: "VOL-", 0xE0E0E01F: "VOL+",
}

#Respond to both remotes (NOTE: cannot have overlapping codes)
SIGNAL_MAP = {}
SIGNAL_MAP.update(SIGNAL_MAP_ADAFRUIT_389_CCC)
SIGNAL_MAP.update(SIGNAL_MAP_LG_CCC)
if not SEND_CONSUMERCONTROL_ONLY:
    SIGNAL_MAP.update(SIGNAL_MAP_ADAFRUIT_389_EXTRAS)
    SIGNAL_MAP.update(SIGNAL_MAP_LG_EXTRAS)
SIGNAL_MAP.update(SIGNAL_MAP_SAMSUNG_EXAMPLE) #Example/test only (only 2 extra signals - leave in)


#=Event handlers
#===============================================================================
class IRDetect(EasyRx):
    def handle_press(self, msg:IRMsg32):
        sig = SIGNAL_MAP.get(msg.bits, None)
        IRcodestr = msg.str_hex()
        if sig is None:
            if USEOPT_MOUSECLICK:
                handled = handle_mouseclick(msg)
                if handled:
                    sig = "Mouse click"
                    print(f"New message: {IRcodestr} ({sig})")
                    return #Special button handled. Don't continue
            print("Unknown message:", IRcodestr)
            return
        print(f"New message: {IRcodestr} ({sig})")
        key = KEYMAP[sig] #A key that can be sent out through USB-HID interface
        key.press()

    def handle_hold(self, msg:IRMsg32):
        print(f"Repeat!") #Doesn't matter what msg is - USB-HID key still held down.

    def handle_release(self, msg:IRMsg32):
        sig = SIGNAL_MAP.get(msg.bits, None)
        if sig is None:
            return
        key = KEYMAP[sig] #A key that can be sent out through USB-HID interface
        key.release()

rx = IRRx(rx_pin)
irdetect = IRDetect(rx, PDE.DecoderNEC(), PDE.DecoderNECRPT(), msgRPT=PDE.IRMSG32_NECRPT)
#Use this one instead for Samsung remotes:
#irdetect = IRDetect(rx, PDE.DecoderSamsung()) #This remote doesn't have a special "repeat" command


#=Main loop
#===============================================================================
print("HELLO24") #DEBUG: Change me to ensure uploaded version matches.
print(f"MediaRemote: ready to receive on pin '{rx_pin}'!")
while True:
    irdetect.process_events()
#end program