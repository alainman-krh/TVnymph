#EasyActuation/CelIRcom.py
#-------------------------------------------------------------------------------
from .Base import now_ms, ms_elapsed, clamp
from CelIRcom.ProtocolsBase import IRMsg32
from CelIRcom.TRxBase import AbstractIRTx
from time import sleep


#=EasyTx
#===============================================================================
class EasyTx: #State machine (FSM) helping to schedule outgoing IR messages
    def __init__(self, tx:AbstractIRTx):
        self.tx = tx

    def msg_send(self, msg:IRMsg32, tadjust=0):
        #tadjust: Compensate for extra delay in loop when sleeping
        tx = self.tx
        pulses = tx.msg_send(msg)
        tsend_ms = ms_elapsed(tx.tx_start, tx.tx_complete)

        #Simplest just to sleep to reach next optimal transmit time:
        msginterval_ms = msg.prot.msginterval_ms
        tleft_ms = msginterval_ms - (tsend_ms + tadjust)
        sleep(clamp(tleft_ms, 0, msginterval_ms)*0.001) #clamp: safety against lockup
        return pulses

#Last line
