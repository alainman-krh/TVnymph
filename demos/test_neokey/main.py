#TVnymph/test_neokey: Test IR control using NeoKey1x4 as input.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRTx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.EasyTx import EasyTx
from EasyActuation.Buttons import EasyNeoKey
from adafruit_neokey.neokey1x4 import NeoKey1x4
from array import array
import board


#=Platform/build-dependent config
#===============================================================================
tx_pin = board.D12 #Metro RP2040
txled_pin = board.LED


#=Main config
#===============================================================================
#Mesages we will be using:
IRPROT = PDE.IRProtocols.NEC
MSG_RPT = PDE.IRMSG32_NECRPT #Special repeat message
MSG_VOLDN = IRMsg32(IRPROT, 0x5EA1D827) #Yamaha: Volume down

#Colors we will be using:
NEOPIXEL_OFF = 0x0
KEYPAD_COLORS = ( #NeoPixel colors assoicated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)

#Inter-message timing
#-------------------------------------------------------------------------------
TPROC_KEYPAD = 60 #ms: Adjust for keypad processing between MSG_RPT

#IO config
#-------------------------------------------------------------------------------
#Connect to IR diode & on-board LED:
tx = IRTx(tx_pin, IRPROT)
txled = IRTx(txled_pin, IRPROT)
easytx = EasyTx(tx)

#Connect to NeoKey object:
i2c_bus = board.I2C() #use default I2C bus
neokey = NeoKey1x4(i2c_bus, addr=0x30)
btn_voldn = EasyNeoKey(neokey, idx=0)


#=Main loop
#===============================================================================
print("TVnymph: initialized (test_neokey)")
print("\nHI0")
while True:
    for i in range(4): #Process all keys
        is_pressed = neokey[i]
        color = KEYPAD_COLORS[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color

    sig = btn_voldn.signals_detect() #Once per loop
    pulsetrain = None
    if sig == btn_voldn.SIG.PRESS:
        pulsetrain = easytx.msg_send(MSG_VOLDN)
        #Neokey takes about 12ms/key to process.
        #(Extra 12ms*4keys breaks timing for 1st NEC "repeat" message)
        pulsetrain = easytx.msg_send(MSG_RPT) #Immediately send 1st repeat to maintain timing (button scans are slow)
        #print("FIRST") #Likely breaks timing for repeats
    elif sig == btn_voldn.SIG.HOLD:
        pulsetrain = easytx.msg_send(MSG_RPT)
        trigger_led = True #Could theoretically send pulse to LED and meet timing
        #print("RPT") #Likely breaks timing for repeats

    trigger_led = False
    if trigger_led:
        #WARN: Sending pulse on LED takes time.
        #(Likely will keep IR:MSG_RPT from working as intended)
        txled.ptrain_sendnative(pulsetrain) #Mirror onto LED

    debug = False #don't show
    if debug and (pulsetrain != None):
        print(pulsetrain)

#Last line
