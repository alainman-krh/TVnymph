#TVnymph:main.py
#-------------------------------------------------------------------------------
from CelIRcom.Base import IRProtocols, IRMsg32, IRMSG32_NECRPT
from CelIRcom.Tx import IRTx_pulseio as IRTx
from adafruit_neokey.neokey1x4 import NeoKey1x4
from array import array
import board
import time


#=Main config
#===============================================================================
#Mesages we will be using:
MSG_RPT = IRMSG32_NECRPT #Special repeat message
MSG_VOLDN = IRMsg32(IRProtocols.NEC, 0x5EA1D827) #Yamaha: Volume down

KEYPAD_VOLDN_IDX = 0 #Index of NeoKey used to send IR messages
KEYPAD_COLORS = ( #NeoPixel colors assoicated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)
NEOPIXEL_OFF = 0x0


#=IO config
#===============================================================================
#Connect to IR diode & on-board LED:
tx = IRTx(board.D12)
tx.io_configure(IRProtocols.NEC)
tx_led = IRTx(board.LED)
tx_led.io_configure(IRProtocols.NEC)

#Connect to NeoKey object:
i2c_bus = board.I2C() #use default I2C bus
neokey = NeoKey1x4(i2c_bus, addr=0x30)


#=Helper tools
#===============================================================================
def now():
    return time.time() * 1000000 #in microseconsd

class Mediator_IRTX: #State machine controlling when we can send IR messages
    STATE_READY = 0
    STATE_WATINGMINDELAY = 1

    def __init__(self, mindelay_ms=100):
        self.state = self.STATE_READY
        self.time_lastused = now()
        self.mindelay = mindelay_ms * 1000 #convert to us (matching now()).

    def state_refresh(self):
        tnow = now()
        tgap = tnow - self.time_lastused
        if tgap >= self.mindelay:
            self.time_lastused = tnow
            self.state = self.STATE_READY

    def signal_message_sent(self):
        #Inform mediator that a message was just sent (completed)
        self.time_lastused = now()
        self.state = self.STATE_WATINGMINDELAY

    def is_ready(self):
        self.state_refresh()
        return self.STATE_READY == self.state

tx_mediator = Mediator_IRTX(mindelay_ms=0*100) #don't wait
state_last = 0


#=Inter-message timing
#===============================================================================
#HACK: Seems like pulseio lib sleeps after sending a message (alters timing of NECRPT messages):
PULSEIO_TSLEEP = 60 #ms: for RP2040
NEC_MSG_TINTERVAL = 110 #ms: Minimum time interval between start of repeated messages
NEC_TMSG = 68 #ms: timespan for sending regular NEC messages
NEC_TRPT = 12 #ms: timespan for sending NEC "repeat" message
#Time to wait after sending messages:
NEC_MSG_TWAIT = NEC_MSG_TINTERVAL-NEC_TMSG-PULSEIO_TSLEEP #ms: regular message
NEC_RPT_TWAIT = NEC_MSG_TINTERVAL-NEC_TRPT-PULSEIO_TSLEEP #ms: repeat
if NEC_MSG_TWAIT < 0:
    texcess = abs(NEC_MSG_TWAIT)
    print(f"WARNING: SW limitations will likely break timing of repeat messages:")
    print(f"         pulseio induces excess delay of {texcess}ms.")
NEC_MSG_TWAIT = max(0, NEC_MSG_TWAIT)*0.001 #convert to sec
NEC_RPT_TWAIT = max(0, NEC_RPT_TWAIT)*0.001 #convert to sec
print("NEC_MSG_TWAIT", NEC_MSG_TWAIT)
print("NEC_RPT_TWAIT", NEC_RPT_TWAIT)


#=Main loop
#===============================================================================
while True:
    color = 0
    for ikey in range(4):
        is_pressed = neokey[ikey]
        color = KEYPAD_COLORS[ikey] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[ikey] = color          

    is_pressed = neokey[KEYPAD_VOLDN_IDX]
    if not is_pressed:
        state_last = 0
    elif tx_mediator.is_ready():
        initial_keypress = (0 == state_last)
        initial_keypress = True #Overwrite

        if initial_keypress:
            (pulses, pulses_us) = tx.send(MSG_VOLDN)
            tx_mediator.signal_message_sent()
            if NEC_MSG_TWAIT > 0:
                time.sleep(NEC_MSG_TWAIT)
            trigger_led = False
            #print("FIRST")
        else:
            (pulses, pulses_us) = tx.send(MSG_RPT)
            tx_mediator.signal_message_sent() #Before sleep
            time.sleep(NEC_RPT_TWAIT)
            trigger_led = True #Could theoretically send pulse to LED and meet timing
            #print("RPT")

        trigger_led = False
        if trigger_led:
            #WARN: Sending pulse on LED takes time.
            #Likely keeps IR-MSG_RPT from working as intended:
            tx_led.pulse.send(pulses_us) #Mirror onto LED
        #print(pulses)
        #time.sleep(.01) #about 100ms between codes
        #print(pulses_us)
        state_last = 1

#Last line