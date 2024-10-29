#demos/PCnymph_IRRxClick: 
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
import board


#=Platform/build-dependent config (Raspberry Pi Pico RP2040)
#===============================================================================
#rx_pin = board.GP16
#rx_pin = board.D9 #Variant: KB2040 "Kee Boar"-based


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
#Mesages we will be detecting:
rx.decoders_setactive([PDE.DecoderNEC(), PDE.DecoderSamsung(), PDE.DecoderNECRPT()])

#Change identifier sent with each code (must match what PCnymph_macroremote expects)
PDE.IRProtocols.NEC.id = "IRNEC"
PDE.IRProtocols.SAMSUNG.id = "IRSAM"
PDE.IRProtocols.NECRPT.id = "IRNEC-RPT"


#=Main loop
#===============================================================================
while True:
    msg:IRMsg32 = rx.msg_read() #Auto prints message when recieves one
    if msg != None:
        #print(msg.str_hex(prefix="")) #Don't send "0x". Minimize data transmission
        print(msg.str_hex()) #DO send "0x".
    #endif