#demos/PCnymph_IR2serial: 
#-------------------------------------------------------------------------------
from CelIRcom.Messaging import IRProtocols, IRMsg32
from CelIRcom.Rx_pulseio import IRRx
import board


#=Platform/build-dependent config
#===============================================================================
rx_pin = board.GP16 #RP2040 nano


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
#Mesages we will be detecting:
rx.protocols_setactive([IRProtocols.NEC, IRProtocols.NECRPT])

#Change identifier sent with each code (must match what PCnymph_macroremote expects)
IRProtocols.NEC.id = "IR"
IRProtocols.NECRPT.id = "IR-RPT"


#=Main loop
#===============================================================================
while True:
    msg:IRMsg32 = rx.msg_read() #Auto prints message when recieves one
    if msg != None:
        print(msg.str_hex(prefix="")) #Don't send "0x". Minimize data transmission
    #endif