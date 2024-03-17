#TVnymph/test_neokey: Test IR control using NeoKey1x4 as input.
#-------------------------------------------------------------------------------
from CelIRcom.Base import IRProtocols, IRMsg32, IRMSG32_NECRPT
from CelIRcom.Tx import IRTx_pulseio as IRTx
from EasyActuation.CelIRcom import EasyTx
from EasyActuation.Buttons import EasyNeoKey
from adafruit_neokey.neokey1x4 import NeoKey1x4
from array import array
import board


#=Main config
#===============================================================================
#Mesages we will be using:
IRPROT = IRProtocols.NEC
MSG_RPT = IRMSG32_NECRPT #Special repeat message
MSG_VOLDN = IRMsg32(IRPROT, 0x5EA1D827) #Yamaha: Volume down

#Colors we will be using:
NEOPIXEL_OFF = 0x0
KEYPAD_COLORS = ( #NeoPixel colors assoicated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)


#=IO config
#===============================================================================
#Connect to IR diode & on-board LED:
tx = IRTx(board.D12, IRPROT)
tx_led = IRTx(board.LED, IRPROT)
easytx = EasyTx(tx)

#Connect to NeoKey object:
i2c_bus = board.I2C() #use default I2C bus
neokey = NeoKey1x4(i2c_bus, addr=0x30)
btn_voldn = EasyNeoKey(neokey, idx=0)


#=Inter-message timing
#===============================================================================
PULSEIO_TSLEEP = 60 #ms: (on RP2040) Seems like pulseio lib sleeps after sending a message.
NEC_TMSG = 68 #ms: timespan for sending regular NEC messages
#Time to wait after sending messages:
TWAIT_MSG = IRPROT.msginterval_ms - (PULSEIO_TSLEEP+NEC_TMSG)
if TWAIT_MSG < 0:
    texcess = abs(TWAIT_MSG)
    print(f"WARNING: SW limitations will likely break timing of repeat messages:")
    print(f"         pulseio induces excess delay of {texcess}ms.")


#=Main loop
#===============================================================================
while True:
    color = 0; pulsetrain = None
    for ikey in range(4):
        is_pressed = neokey[ikey]
        color = KEYPAD_COLORS[ikey] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[ikey] = color          

    sig = btn_voldn.signals_detect() #Once per loop
    if sig == btn_voldn.SIG.PRESS:
        pulsetrain = easytx.msg_send(MSG_VOLDN)
        trigger_led = False
        #print("FIRST") #Likely breaks timing for repeats
    elif sig == btn_voldn.SIG.HOLD:
        pulsetrain = easytx.msg_send(MSG_RPT)
        trigger_led = True #Could theoretically send pulse to LED and meet timing
        #print("RPT") #Likely breaks timing for repeats

    trigger_led = False
    if trigger_led:
        #WARN: Sending pulse on LED takes time.
        #Likely keeps IR-MSG_RPT from working as intended:
        tx_led.pulsetrain_send(pulsetrain) #Mirror onto LED

    pulsetrain = None #Don't show
    if pulsetrain != None:
        print(pulsetrain)

#Last line
