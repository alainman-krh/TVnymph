#demos/TVnymph_livingroom2: More complex example (TV+AV/RX+BRAY+PC).
#-------------------------------------------------------------------------------
from MyState.CtrlInputs.Buttons import EasyButton
from EasyCktIO.adafruit_neokey import EasyNeoKey_1x4
from adafruit_neokey.neokey1x4 import NeoKey1x4
from CelIRcom.TRx_pulseio import IRTx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
import CelIRcom.Protocols_PLE as PLE
from CelIRcom.EasyIRTx import EasyTx, IRSequence
import board


#=Platform/build-dependent config (Adafruit Metro RP2040)
#===============================================================================
KEYPAD_ADDR = 0x30 #I2C address
PIN_TX = board.D12
BUS_I2C = board.I2C() #use default I2C bus (NeoKey)


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
    INPUT_APPLETV = HDMI3

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
TWAIT_POWERON_SKIP = 0.2 #Maximum wait time if we are skipping power-on
#RX messages need to be run twice
CONFIG_OFF = IRSequence("OFF",
    (
        #MSG_BRAY.OFF seems unresponsive when sent once. Sort of works if sent twice.
        #Sony remote sends command 3 times with timing below. Seems more robust this way:
        MSG_RX.OFF, 0.2, MSG_TV.OFF, 0.2, MSG_BRAY.OFF, MSG_BRAY.OFF, 0.125, MSG_BRAY.OFF, 0.2,
    )
)
CONFIG_NETFLIX = IRSequence("Netflix",
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.STR_NETFLIX, 0.2,
        MSG_RX.INPUT_TVAUDIO, 0.2, #Directly running on TV
    )
)
CONFIG_APPLETV = IRSequence("Apple TV",
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_APPLETV, 0.2,
        MSG_RX.INPUT_TVAUDIO, 0.2, #Directly connected to TV
    )
)
CONFIG_BRAY = IRSequence("Blu-ray",
    #Not 4K. Might as well connect through RX.
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, 0.2, MSG_BRAY.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, 0.2,
        MSG_RX.INPUT_BRAY, 0.2, #Connected through RX
    )
)
CONFIG_GAMEPC = IRSequence("Gaming PC",
    #Connected to RX directly to get discrete-channel surround (PC games rarely generate Dolby mix).
    #No IR reciever to turn on/off PC at the moment :(.
    (
        MSG_RX.ON, 0.2, MSG_TV.ON, TWAIT_POWERON,
        MSG_TV.INPUT_RX, 0.2,
        MSG_RX.INPUT_GAMEPC, 0.2, #Connected through RX
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
#NeoKey/Keypad configuration
NEOPIXEL_OFF = 0x0
KEYPAD_COLORASSIGN = ( #NeoPixel colors associated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)
KEYPAD_TASKASSIGN = (
    CONFIG_OFF, CONFIG_NETFLIX, CONFIG_GAMEPC, CONFIG_BRAY
)


#=IO config
#===============================================================================
#Connect to IR diode & on-board LED:
tx = IRTx(PIN_TX, PDE.IRProtocols.NEC) #ISSUE: Can't switch between protocols (will use same freq, etc).
easytx = EasyTx(tx) #Controls timing between message transmissions

#Connect to NeoKey object:
neokey = NeoKey1x4(BUS_I2C, addr=KEYPAD_ADDR)


#=Buttons/Event handlers
#===============================================================================
class NeoKey_IRSend(EasyButton):
    """Use `easytx` to send IR message sequence when NeoKey is pressed"""
    def runseq(self, idx, poweron_skip=False):
        irsequence = KEYPAD_TASKASSIGN[idx]
        print(f"Switching to mode: {irsequence.id}")        
        sleep_max = None
        if poweron_skip:
            sleep_max = TWAIT_POWERON_SKIP
        easytx.execute(irsequence, sleep_max=sleep_max)
        print(f"Mode switch complete: {irsequence.id}")

    def handle_press(self, idx):
        self.runseq(idx, poweron_skip=True)
    def handle_longpress(self, idx):
        self.runseq(idx)
ez_neokey = EasyNeoKey_1x4(neokey, NeoKey_IRSend)


#=Main loop
#===============================================================================
print("\nTVnymph: initialized")
print("HI2") #Debug: see if code was uploaded
while True:
    for i in range(4): #Process all keys
        key:NeoKey_IRSend = ez_neokey.keys[i]
        is_pressed = key.btnsense.isactive()
        color = KEYPAD_COLORASSIGN[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color
        key.process_giveninputs(is_pressed)
#Last line
