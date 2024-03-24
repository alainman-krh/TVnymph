#CelIRcom/Rx.py
#-------------------------------------------------------------------------------
from .Protocols import IRProtocols, array_ticks
import pulseio


#=IRRx
#===============================================================================

#IRRx_pulseio
#-------------------------------------------------------------------------------
class IRRx_pulseio:
    def __init__(self, pin, prot, autoclear=True):
        #autoclear: auto-clear recieve queue before we ask to read a new message
        #super().__init__()
        self.autoclear = autoclear
        self.io_configure(pin, prot, maxlen=120)

    def io_configure(self, pin, prot, maxlen):
        #pulseio receiver:
        self.piorx = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def queue_clear(self):
        #clear recieve queue, ignoring any
        return

#Last line