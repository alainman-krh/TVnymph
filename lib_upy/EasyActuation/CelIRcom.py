#EasyActuation/CelIRcom.py
#-------------------------------------------------------------------------------
from .Base import now_ms
from time import sleep


#=EasyTx
#===============================================================================
class EasyTx: #State machine (FSM) helping to schedule outgoing IR messages
    def __init__(self, tx): #irtx: CelIRcom.IRTx
        self.tx = tx

    def msg_send(self, msg, tadjust=0):
        #tadjust: Compensate for extra delay in loop when sleeping
        tx = self.tx
        pulses = tx.msg_send(msg)
        tsend_ms = tx.tx_complete - tx.tx_start

        #Simplest just to sleep to reach next optimal transmit time:
        trmg_ms = msg.prot.msginterval_ms - (tsend_ms + tadjust)
        sleep(max(0, trmg_ms)*0.001)
        return pulses

#Last line
