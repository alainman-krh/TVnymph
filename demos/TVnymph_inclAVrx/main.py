#TVnymph/TVnymph_inclAVrx: Typical example (this one controls an AV receiver).
#-------------------------------------------------------------------------------
from CelIRcom.Tx_pulseio import IRTx
from CelIRcom.Protocols import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from EasyActuation.CelIRcom import EasyTx
from EasyActuation.Buttons import EasyNeoKey, BtnSig
from adafruit_neokey.neokey1x4 import NeoKey1x4
from array import array
from time import sleep
import board


#=Platform/build-dependent config
#===============================================================================
tx_pin = board.D12 #Metro RP2040
#txled_pin = board.LED
i2c_bus = board.I2C() #use default I2C bus (NeoKey)


#=Main config: Messages
#===============================================================================
#Mesages we will be using:
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
    PROT = PDE.IRProtocols.NEC #NO: SONY

    #Sony BluRay:
    ON = None #IRMsg32(PROT, 0x0)
    OFF = None #IRMsg32(PROT, 0x0)


#=OpMode
#===============================================================================
class OpMode:
    def __init__(self, id, ctrlseq):
        self.id = id
        self.ctrlseq = ctrlseq

    def activate(self, irtx:EasyTx):
        print(f"Switching to mode: {self.id}")
        for step in self.ctrlseq:
            if step is None:
                continue

            T = type(step)
            if T in (int, float):
                tsleep = step
                sleep(tsleep)
            elif T == IRMsg32:
                irtx.msg_send(step)
        print(f"Mode switch complete: {self.id}")


#=Operating modes
#===============================================================================
TWAIT_POWERON = 5 #Long enough for TV/RX/etc to recieve signals (but not too long)
#RX messages need to be run twice
OPMODE_OFF = OpMode("OFF",
    (
        MSG_RX.OFF, MSG_RX.OFF, 0.1, MSG_TV.OFF, 0.1, MSG_BRAY.OFF, 0.1,
    )
)
OPMODE_SAT = OpMode("SAT",
    (
        MSG_RX.ON, MSG_RX.ON, 0.1, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_SAT, 0.1,
        MSG_RX.INPUT_TVAUDIO, MSG_RX.INPUT_TVAUDIO, 0.1,
    )
)
OPMODE_BRAY = OpMode("Blu-ray",
    #Not 4K. Might as well connect through RX.
    (
        MSG_RX.ON, MSG_RX.ON, 0.1, MSG_TV.ON, 0.1, MSG_BRAY.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, 0.1,
        MSG_RX.INPUT_BRAY, MSG_RX.INPUT_BRAY, 0.1,
    )
)
OPMODE_GAMEPC = OpMode("Gaming PC",
    #Connected to RX directly to get discrete-channel surround (PC games rarely generate Dolby mix).
    #No IR reciever to turn on/off PC at the moment :(.
    (
        MSG_RX.ON, MSG_RX.ON, 0.1, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, MSG_TV.INPUT_RX, 0.1,
        MSG_RX.INPUT_GAMEPC, MSG_RX.INPUT_GAMEPC, 0.1,
    )
)

#Future operation modes (need more buttons):
#- STREAM_x: One of N video streaming services
#- STREAM_AUDx: One of N audio streaming services
#- RADIO_FM: FM Radio
#- GAMECONSOLE_x: One of N video gaming consoles
#- HTPC: Home theatre PC


#=Main config
#===============================================================================
KEYPAD_MODEASSIGN = (
    OPMODE_OFF, OPMODE_SAT, OPMODE_BRAY, OPMODE_GAMEPC
)

#Colors we will be using:
NEOPIXEL_OFF = 0x0
KEYPAD_COLORS = ( #NeoPixel colors assoicated with each NeoKey:
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
print("\nHI3") #Debug: see if code was uploaded
while True:
    for i in range(4): #Process all keys
        is_pressed = neokey[i]
        color = KEYPAD_COLORS[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color

        sig = easykey[i].signals_detect() #Check only once per loop
        if sig == BtnSig.PRESS:
            mode = KEYPAD_MODEASSIGN[i]
            mode.activate(easytx)
#Last line
