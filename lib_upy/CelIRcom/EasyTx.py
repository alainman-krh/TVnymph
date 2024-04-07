#CelIRcom/EasyTx
#-------------------------------------------------------------------------------
from .Timebase import now_ms, ms_elapsed, ms_addwrap, clamp
from .ProtocolsBase import IRMsg32
from .TRxBase import AbstractIRTx
from time import sleep


#=IRSequence
#===============================================================================
class IRSequence:
    def __init__(self, id, ctrlseq):
        #ctrlseq: a list of IR messages, and sleep intervals
        self.id = id
        self.ctrlseq = ctrlseq


#=EasyTx
#===============================================================================
class EasyTx: #State machine (FSM) helping to schedule outgoing IR messages
    def __init__(self, tx:AbstractIRTx):
        self.tx = tx
        self.tx_start_last = now_ms()

    def msg_send(self, msg:IRMsg32):
        #Wait `msgintervalMS` between sending messages:
        msgintervalMS = msg.prot.msgintervalMS
        elapsed = ms_elapsed(self.tx_start_last, now_ms())
        tleft_ms = msgintervalMS - elapsed
        #print("msgintervalMS", msgintervalMS); print("tleft_ms", tleft_ms) #DEBUG
        #Simplest just to sleep to reach next optimal transmit time:
        sleep(clamp(tleft_ms, 0, msgintervalMS)*0.001) #clamp: safety against lockup

        tx = self.tx
        #t0 = now_ms()
        pulses = tx.msg_send(msg)
        self.tx_start_last = tx.tx_start
        #tbuild_ms =  ms_elapsed(t0, tx.tx_start); print("tbuild_ms", tbuild_ms) #DEBUG
        #tsend_ms = ms_elapsed(tx.tx_start, tx.tx_complete); print("tsend_ms", tsend_ms) #DEBUG
        return pulses

#-------------------------------------------------------------------------------
    def execute(self, seq:IRSequence):
        for step in seq.ctrlseq:
            if step is None:
                continue

            T = type(step)
            if T in (int, float):
                tsleep = step
                sleep(tsleep)
            elif T == IRMsg32:
                self.msg_send(step)
        return

#Last line
