#CelIRcom/Tx_pulseio.py: IR tx implementation using pulseio backend.
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks
from .Protocols import ptrain_pulseio as ptrain_native #Native... for this transmitter
from .Tx import AbstractIRTx
import pulseio

#TODO: Create/re-use buffer ptrain_native[PulseCount_Max]


#IRTx
#-------------------------------------------------------------------------------
class IRTx(AbstractIRTx):
    def __init__(self, pin, prot):
        super().__init__()
        self.io_configure(pin, prot)

    def io_configure(self, pin, prot):
        #pulseio transmitter:
        self.piotx = pulseio.PulseOut(pin, frequency=prot.f, duty_cycle=prot.duty_int16)

    def ptrain_buildnative(self, ptrainK, tickT):
        return ptrain_native(abs(p)*tickT for p in ptrainK) #TODO: NOALLOC

    def _ptrain_sendnative_immediate(self, ptrainNat):
        self.piotx.send(ptrainNat)

#Last line
