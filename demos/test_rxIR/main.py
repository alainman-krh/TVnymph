#demos/test_rxIR: Test receiving/decoding IR signals.
#-------------------------------------------------------------------------------
from CelIRcom.Messaging import IRProtocols, IRMsg32, IRMSG32_NECRPT
from CelIRcom.Rx_pulseio import IRRx, ticks_ms
from time import sleep
import board
#import uctypes


#=Main config
#===============================================================================
#Mesages we will be using:
IRPROT = IRProtocols.NEC
rx = IRRx(board.GP16, IRPROT)


#=Main loop
#===============================================================================
print("IR: ready to receive!")
print("\nHI1")
while True:
    rx.msg_read() #Auto prints message when recieves one
    now = ticks_ms()
    #print(now, uctypes.sizeof(3, uctypes.LITTLE_ENDIAN))
    sleep(1)
