#demos/test_rxIR: Test receiving/decoding IR signals.
#-------------------------------------------------------------------------------
from CelIRcom.Messaging import IRProtocols, IRMsg32, IRMSG32_NECRPT
from CelIRcom.Rx import IRRx_pulseio
from time import sleep
import board


#=Main config
#===============================================================================
#Mesages we will be using:
IRPROT = IRProtocols.NEC
rx = IRRx_pulseio(board.GP16, IRPROT)


#=Main loop
#===============================================================================
print("IR: ready to receive!")
print("\nHI0")
while True:
    rx.msg_read() #Auto prints message when recieves one
    sleep(1)
