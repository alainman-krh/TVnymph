#CelIRcom/Tx.py
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks
from .Encoder_STD1 import Encoder_STD1 #TODO: Don't reference a decoder
from .Timebase import now_ms

#TODO: Create/re-use buffer ptrain_native[PulseCount_Max]

#=IRTx
#===============================================================================
class AbstractIRTx:
    def __init__(self):
        self.tx_start = now_ms() #ms
        self.tx_complete = now_ms() #ms
        self.ptrainK = ptrain_ticks((0,)*PulseCount_Max.PACKET) #Buffer
        self.encoder = Encoder_STD1() #TODO: not here!!!

    #Implement interface:
    #---------------------------------------------------------------------------
    #def ptrain_buildnative(self, ptrainK, tickT):
    #def _ptrain_sendnative_immediate(self, ptrainNat):
    #---------------------------------------------------------------------------

    def ptrain_sendnative(self, ptrainNat):
        """Send pulse train ()"""
        self.tx_start = now_ms()
        self.tx_complete = self.tx_start
        self._ptrain_sendnative_immediate(ptrainNat)
        self.tx_complete = now_ms()
        return ptrainNat

    def msg_send(self, msg):
        #NOTE: ptrain can be any format most practical for a given implementation
        N = self.encoder.build(self.ptrainK, msg)
        ptrainK = memoryview(self.ptrainK)[:N]
        ptrainNat = self.ptrain_buildnative(ptrainK, msg.prot.tickT)
        return self.ptrain_sendnative(ptrainNat)

#Last line
