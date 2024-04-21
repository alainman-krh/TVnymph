#demos/TVnymph_livingroom1: Typical example (TV+SAT+BRAY).
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRTx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
import CelIRcom.Protocols_PLE as PLE
from CelIRcom.EasyTx import EasyTx, IRSequence
from EasyActuation.Buttons import EasyNeoKey, BtnSig
from adafruit_neokey.neokey1x4 import NeoKey1x4
import board


#=Platform/build-dependent config
#===============================================================================
tx_pin = board.D12 #Metro RP2040
#txled_pin = board.LED
i2c_bus = board.I2C() #use default I2C bus (NeoKey)


#=IR message definitions (captured from remote controls)
#===============================================================================
class MSG_TV: #Namespace (LG UK6090PUA)
    PROT = PDE.IRProtocols.NEC
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0x20DF23DC)
    OFF = IRMsg32(PROT, 0x20DFA35C)
    HOME = IRMsg32(PROT, 0x20DF3EC1)
    MENU_SMART = IRMsg32(PROT, 0x20DF3EC1)
    HDMI1 = IRMsg32(PROT, 0x20DF738C)
    HDMI2 = IRMsg32(PROT, 0x20DF33CC)
    HDMI3 = IRMsg32(PROT, 0x20DF9768)
    TVTUNER = IRMsg32(PROT, 0x20DF6B94)
    STR_NETFLIX = IRMsg32(PROT, 0x20DF6A95)
    STR_AMAZON = IRMsg32(PROT, 0x20DF3AC5)

    #Aliases:
    INPUT_SAT = HDMI1
    INPUT_BRAY = HDMI3

#Satellite: Using a different protocol. Power toggle not found. Let's ignore!

class MSG_BRAY: #Namespace (Sony BDP-S1700)
    #Looks like BDP-S1700 expects IR messages to be transmitted 3 times:
    #2nd time: 45 ms after the previous. 3rd time: 125ms after the previous.
    #-"OFF" message appears to be more likely to ignore badly timed sequences.
    PROT = PLE.IRProtocols.SONY20

    ON = IRMsg32(PROT, 0x8B4B8)
    OFF = IRMsg32(PROT, 0x0B4B8)


#=Configuration sequences for different "operating modes"
#===============================================================================
TWAIT_POWERON = 5 #Long enough for TV/RX/etc to recieve signals (but not too long)
#RX messages need to be run twice
CONFIG_OFF = IRSequence("OFF",
    (
        #MSG_BRAY.OFF seems unresponsive when sent once. Sort of works if sent twice.
        #Sony remote sends command 3 times with timing below. Seems more robust this way:
        MSG_TV.OFF, 0.2, MSG_BRAY.OFF, MSG_BRAY.OFF, 0.125, MSG_BRAY.OFF, 0.2,
    )
)
CONFIG_SAT = IRSequence("Satellite TV",
    (
        MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_SAT, 0.2,
    )
)
CONFIG_NETFLIX = IRSequence("Netflix",
    (
        MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.STR_NETFLIX, 0.2,
    )
)
CONFIG_BRAY = IRSequence("Blu-ray",
    #Not 4K. Might as well connect through RX.
    (
        MSG_TV.ON, 0.2, MSG_BRAY.ON, TWAIT_POWERON,
        MSG_TV.INPUT_BRAY, 0.2,
    )
)


#=Keypad controls
#===============================================================================
KEYPAD_TASKASSIGN = (
    CONFIG_OFF, CONFIG_SAT, CONFIG_NETFLIX, CONFIG_BRAY,
)

#Colors we will be using:
NEOPIXEL_OFF = 0x0
KEYPAD_COLORASSIGN = ( #NeoPixel colors associated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)


#=IO config
#===============================================================================
#Connect to IR diode & on-board LED:
tx = IRTx(tx_pin, PDE.IRProtocols.NEC) #ISSUE: Can't switch between protocols (will use same freq, etc).
easytx = EasyTx(tx)

#Connect to NeoKey object:
neokey = NeoKey1x4(i2c_bus, addr=0x30)
easykey = tuple(EasyNeoKey(neokey, idx=i) for i in range(4))


#=Main loop
#===============================================================================
print("TVnymph: initialized")
print("\nHI0") #Debug: see if code was uploaded
while True:
    for i in range(4): #Process all keys
        is_pressed = neokey[i]
        color = KEYPAD_COLORASSIGN[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color

        sig = easykey[i].signals_detect() #Check only once per loop
        if sig == BtnSig.PRESS:
            irsequence = KEYPAD_TASKASSIGN[i]
            print(f"Switching to mode: {irsequence.id}")
            easytx.execute(irsequence)
            print(f"Mode switch complete: {irsequence.id}")
#Last line
