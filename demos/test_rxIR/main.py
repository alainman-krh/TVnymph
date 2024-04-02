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

from array import array
dbg_code = array('H', [65535, 9015, 4440, 591, 530, 585, 538, 588, 1659, 593, 529, 616, 507, 619, 504, 622, 500, 615, 508, 618, 1628, 594, 1652, 589, 534, 592, 1654, 587, 1660, 592, 1654, 587, 1660, 592, 1655, 586, 537, 589, 1657, 584, 539, 587, 535, 591, 531, 585, 538, 587, 535, 591, 531, 595, 1652, 589, 533, 593, 1653, 589, 1657, 584, 1662, 590, 1656, 585, 1662, 589, 1657, 585, 40084, 8998, 2212, 587])
done = False


#=Main loop
#===============================================================================
print("IR: ready to receive!")
print("\nHI1")
while True:
    if not done:
        print(dbg_code)
        rx.msg_decode_any(dbg_code)
        done = True
        print("DONE")

    t0 = ticks_ms()
    msg:IRMsg32 = rx.msg_read() #Auto prints message when recieves one
    t1 = ticks_ms()
    if msg != None:
        print(f"Protocol detected: {msg.prot.id}")
        print("readtime:", t1-t0)
    #now = ticks_ms()
    #print(now, uctypes.sizeof(3, uctypes.LITTLE_ENDIAN))
    #sleep(1)
