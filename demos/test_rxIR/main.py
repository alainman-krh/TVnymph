#demos/test_rxIR: Test receiving/decoding IR signals.
#-------------------------------------------------------------------------------
from CelIRcom.Messaging import IRProtocols, IRMsg32, IRMSG32_NECRPT
from CelIRcom.Rx_pulseio import IRRx, ticks_ms
from time import sleep
import board
#import uctypes


#=Platform/build-dependent config
#===============================================================================
rx_pin = board.GP16 #RP2040 nano


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
#Mesages we will be detecting:
rx.protocols_setactive([IRProtocols.NEC, IRProtocols.NECRPT])


#=Main loop
#===============================================================================
print("IR: ready to receive!")
print("\nHI1")
while True:
    rx.msg_read() #Auto prints message when recieves one
    now = ticks_ms()
    #print(now, uctypes.sizeof(3, uctypes.LITTLE_ENDIAN))
    sleep(1)
