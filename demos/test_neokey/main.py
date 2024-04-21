#demos/test_neokey: Test IR control using NeoKey1x4 as input.
#-------------------------------------------------------------------------------
from EasyActuation.Buttons import EasyButton_EventHandler, EasyNeoKey_1x4
from adafruit_neokey.neokey1x4 import NeoKey1x4
from CelIRcom.TRx_pulseio import IRTx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.EasyTx import EasyTx
from array import array
import board


#=Platform/build-dependent config
#===============================================================================
#Assume Metro RP2040:
KEYPAD_ADDR = 0x30 #I2C address
PIN_TX = board.D12
PIN_TXLED = board.LED
BUS_I2C = board.I2C() #use default I2C bus


#=Main config
#===============================================================================
TRIGGER_LED = True

#Mesages we will be using:
IRPROT = PDE.IRProtocols.NEC
MSG_RPT = PDE.IRMSG32_NECRPT #Special repeat message
MSG_VOLUP = IRMsg32(IRPROT, 0x5EA1D827) #Yamaha: Volume up #TODO: FIXME!
MSG_VOLDN = IRMsg32(IRPROT, 0x5EA1D827) #Yamaha: Volume down

#NeoKey/Keypad configuration
NEOPIXEL_OFF = 0x0
KEYPAD_COLORS = ( #NeoPixel colors assoicated with each NeoKey:
    0xFF0000, 0xFFFF00, 0x00FF00, 0x00FFFF
)
KEYPAD_MESSAGES = ( #IR messages assoicated with each NeoKey:
    MSG_VOLUP, MSG_VOLDN, MSG_VOLUP, MSG_VOLDN
)


#=IO config
#===============================================================================
#Connect to IR diode & on-board LED:
tx = IRTx(PIN_TX, IRPROT) #Configure to transmit
txled = IRTx(PIN_TXLED, IRPROT) #Configure to mirror transmitter
ez_tx = EasyTx(tx) #Controls timing between message transmissions

#Connect to NeoKey object:
neokey = NeoKey1x4(BUS_I2C, addr=KEYPAD_ADDR)


#=Buttons/Event handlers
#===============================================================================
class Handler_IRSend(EasyButton_EventHandler):
    def handle_press(self, id):
        msg = KEYPAD_MESSAGES[id] #Id should always be with range
        pulsetrain = ez_tx.msg_send(msg)
        #Neokey takes about 12ms/key to process.
        #(Extra 12ms*4keys breaks timing for 1st NEC "repeat" message)
        pulsetrain = ez_tx.msg_send(MSG_RPT) #Immediately send 1st repeat to maintain timing (button scans are slow)
        if TRIGGER_LED:
            txled.ptrain_sendnative(pulsetrain) #Mirror onto LED... but only shorter RPT signal
        print(f"{msg.str_hex()} (id={id})")

    def handle_hold(self, id):
        pulsetrain = ez_tx.msg_send(MSG_RPT)
        if TRIGGER_LED:
            txled.ptrain_sendnative(pulsetrain) #Mirror onto LED
        print(f"RPT (id={id})")
ez_neokey = EasyNeoKey_1x4(neokey, Handler_IRSend())


#=Main loop
#===============================================================================
print("\nTVnymph/test_neokey: initialized")
print("HI0")
while True:
    #Simplified way of 
    for i in range(4): #Process all keys
        is_pressed = neokey[i]
        color = KEYPAD_COLORS[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color
    ez_neokey.process_events()

#Last line
