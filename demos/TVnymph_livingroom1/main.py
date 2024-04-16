#TVnymph/TVnymph_livingroom1: Typical example (this one controls an AV receiver).
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
class MSG_TV: #Namespace (Samsung TV)
    PROT = PDE.IRProtocols.SAMSUNG
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0xE0E09966)
    OFF = IRMsg32(PROT, 0xE0E019E6)
    HDMI1 = IRMsg32(PROT, 0xE0E09768)
    HDMI2 = IRMsg32(PROT, 0xE0E07D82)
    HDMI3 = IRMsg32(PROT, 0xE0E043BC)
    STR_NETFLIX = IRMsg32(PROT, 0xE0E0CF30)
    STR_PRIME = IRMsg32(PROT, 0xE0E02FD0)
    STR_SAMSUNGTV = IRMsg32(PROT, 0xE0E0D629)

    #Aliases:
    INPUT_RX = HDMI1
    INPUT_HTPC = HDMI2
    INPUT_SAT = HDMI3

class MSG_RX: #Namespace (Yamaha RX-V475)
    PROT = PDE.IRProtocols.NEC
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0x5EA1B847)
    OFF = IRMsg32(PROT, 0x5EA17887)
    HDMI1 = IRMsg32(PROT, 0x5EA1E21C)
    HDMI2 = IRMsg32(PROT, 0x5EA152AC)
    HDMI3 = IRMsg32(PROT, 0x5EA1B24C)
    HDMI4 = IRMsg32(PROT, 0x5EA10AF4)
    AV4 = IRMsg32(PROT, 0x5EA13AC4)
    AM = IRMsg32(PROT, 0xFE80AA54)
    FM = IRMsg32(PROT, 0xFE801AE4)

    #Aliases:
    INPUT_TVAUDIO = AV4
    INPUT_BRAY = HDMI1
    INPUT_GAMEPC = HDMI3

class MSG_BRAY: #Namespace
    PROT = PLE.IRProtocols.SONY20
    #Looks like Sony20 protocol expects the messages to be transmitted 3 times:
    #2nd time: 45 ms after the previous. 3rd time: 125ms after the previous.
    #"OFF" message appears to be more likely to ignore badly timed sequences

    #Sony BluRay (BDP-S1700):
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
        MSG_RX.OFF, 0.2, MSG_TV.OFF, 0.2, MSG_BRAY.OFF, MSG_BRAY.OFF, 0.125, MSG_BRAY.OFF, 0.2,
    )
)
CONFIG_SAT = IRSequence("SAT",
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_SAT, 0.2,
        MSG_RX.INPUT_TVAUDIO, 0.2,
    )
)
CONFIG_BRAY = IRSequence("Blu-ray",
    #Not 4K. Might as well connect through RX.
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, 0.2, MSG_BRAY.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, 0.2,
        MSG_RX.INPUT_BRAY, 0.2,
    )
)
CONFIG_GAMEPC = IRSequence("Gaming PC",
    #Connected to RX directly to get discrete-channel surround (PC games rarely generate Dolby mix).
    #No IR reciever to turn on/off PC at the moment :(.
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, 0.2,
        MSG_RX.INPUT_GAMEPC, 0.2,
    )
)

#Future operation modes (need more buttons):
#- STREAM_x: One of N video streaming services
#- STREAM_AUDx: One of N audio streaming services
#- RADIO_FM: FM Radio
#- GAMECONSOLE_x: One of N video gaming consoles
#- HTPC: Home theatre PC


#=Keypad controls
#===============================================================================
KEYPAD_TASKASSIGN = (
    CONFIG_OFF, CONFIG_SAT, CONFIG_BRAY, CONFIG_GAMEPC
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
print("\nHI6") #Debug: see if code was uploaded
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
