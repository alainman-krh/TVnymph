#TVnymph/test_neokey: Test IR control using NeoKey1x4 as input.
#-------------------------------------------------------------------------------
from CelIRcom.Messaging import IRProtocols, IRMsg32, IRMSG32_NECRPT
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
TPROC_KEYPAD = 60 #ms: Adjust for keypad processing between MSG_RPT
TADJ_RPT = TPROC_KEYPAD #ms: Adjust for loop delays between MSG_RPT


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
        pulsetrain = easytx.msg_send(MSG_RPT, tadjust=TADJ_RPT) #Immediately send 1st repeat to maintin timing
        #print("FIRST") #Likely breaks timing for repeats
    elif sig == btn_voldn.SIG.HOLD:
        pulsetrain = easytx.msg_send(MSG_RPT, tadjust=TADJ_RPT)
        trigger_led = True #Could theoretically send pulse to LED and meet timing
        #print("RPT") #Likely breaks timing for repeats

    trigger_led = False
    if trigger_led:
        #WARN: Sending pulse on LED takes time.
        #(Likely will keep IR:MSG_RPT from working as intended)
        tx_led.pulsetrain_send(pulsetrain) #Mirror onto LED

    debug = False #don't show
    if debug and (pulsetrain != None):
        print(pulsetrain)

#Last line
