#EasyActuation/CelIRcom.py
#-------------------------------------------------------------------------------
from .Base import ticks_ms
from time import sleep


#=EasyTx
#===============================================================================
class EasyTx: #State machine (FSM) helping to schedule outgoing IR messages
    def __init__(self, tx): #irtx: CelIRcom.IRTx
        self.tx = tx

    def msg_send(self, msg):
        tx = self.tx
        pulses = tx.msg_send(msg)
        tsend_ms = tx.tx_complete - tx.tx_start

        #Simplest just to sleep to reach next optimal transmit time:
        trmg_ms = msg.prot.msginterval_ms - tsend_ms
        #print("tsend_ms", tsend_ms)
        #print("trmg_ms", trmg_ms)
        #t0 = ticks_ms()
        sleep(max(0, trmg_ms)*0.001)
        #t1 = ticks_ms()
        #print("t1-t0", t1-t0)
        return pulses

#Last line
