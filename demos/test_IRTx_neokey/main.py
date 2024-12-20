#demos/test_IRTx_neokey: Test IRTx control using NeoKey1x4 as input.
#-------------------------------------------------------------------------------
from MyState.CtrlInputs.Buttons import EasyButton
from EasyCktIO.adafruit_neokey import EasyNeoKey_1x4
from adafruit_neokey.neokey1x4 import NeoKey1x4
from CelIRcom.TRx_pulseio import IRTx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
from CelIRcom.EasyIRTx import EasyTx
from array import array
import board


#=Platform/build-dependent config (Adafruit Metro RP2040)
#===============================================================================
KEYPAD_ADDR = 0x30 #I2C address
PIN_TX = board.D12
PIN_TXLED = board.LED
BUS_I2C = board.I2C() #use default I2C bus


#=Main config
#===============================================================================
TRIGGER_LED = True; LOG_MSG = False #Might cause timing issues (I2C com is slow)

#Mesages we will be using:
IRPROT = PDE.IRProtocols.NEC
MSG_RPT = PDE.IRMSG32_NECRPT #Special repeat message
MSG_VOLUP = IRMsg32(IRPROT, 0x5EA158A7) #Yamaha: Volume up
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
txled = IRTx(PIN_TXLED, IRPROT) #Configure to mirror transmitter (prolongs "main loop" runtime)
ez_tx = EasyTx(tx) #Controls timing between message transmissions

#Connect to NeoKey object:
neokey = NeoKey1x4(BUS_I2C, addr=KEYPAD_ADDR)


#=Buttons/Event handlers
#===============================================================================
class NeoKey_IRSend(EasyButton):
    """Use `easytx` to send IR message sequence when NeoKey is pressed"""
    def handle_press(self, idx):
        msg = KEYPAD_MESSAGES[idx] #idx should always be within range
        pulsetrain = ez_tx.msg_send(msg)
        #Neokey takes about 12ms/key to process.
        #(Extra 12ms*4keys breaks timing for 1st NEC "repeat" message)
        pulsetrain = ez_tx.msg_send(MSG_RPT) #Immediately send 1st repeat to maintain timing (button scans are slow)
        if TRIGGER_LED:
            txled.ptrain_sendnative(pulsetrain) #Mirror onto LED... but only shorter RPT signal
        if LOG_MSG:
            print(f"{msg.str_hex()} (idx={idx})")

    def handle_hold(self, idx):
        pulsetrain = ez_tx.msg_send(MSG_RPT)
        if TRIGGER_LED:
            txled.ptrain_sendnative(pulsetrain) #Mirror onto LED
        if LOG_MSG:
            print(f"RPT (idx={idx})")
ez_neokey = EasyNeoKey_1x4(neokey, NeoKey_IRSend)


#=Main loop
#===============================================================================
print("\nTVnymph/test_IRTx_neokey: initialized")
print("HI0")
while True:
    #Simplified way of 
    for i in range(4): #Process all keys
        key:NeoKey_IRSend = ez_neokey.keys[i]
        is_pressed = key.btnsense.isactive()
        color = KEYPAD_COLORS[i] if is_pressed else NEOPIXEL_OFF
        neokey.pixels[i] = color
        key.process_giveninputs(is_pressed)

#Last line
