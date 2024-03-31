#CelIRcom/Rx.py
#-------------------------------------------------------------------------------
from .Protocols import IRProtocols, array_ticks, array_pulses, IRMSG_TMAX_MS
from adafruit_ticks import ticks_ms
import pulseio

#TODO: Request that pulseio register start time of first pulse somehow.


#=IRRx
#===============================================================================

#IRRx
#-------------------------------------------------------------------------------
class IRRx:
    def __init__(self, pin, prot, doneT_ms=10, msgmax_ms=IRMSG_TMAX_MS, autoclear=True):
        #doneT_ms: period of inactivity used to detect end of message transmission.
        #autoclear: auto-clear recieve queue before we ask to read a new message
        #super().__init__()
        doneT_ms = max(10, doneT_ms) #No less than 10ms
        self.doneT_us = doneT_ms * 1_000 #Code needs us: Cache-it!
        #self.doneT_ms = max(1, round((doneT_us+500)//1_000)) #Some code needs ms: Cache-it!
        self.msgmax_ms = msgmax_ms
        self.autoclear = autoclear
        self.read_last = ticks_ms()
        self.io_configure(pin, prot, maxlen=120)
        self.reset()

    def io_configure(self, pin, prot, maxlen):
        #pulseio receiver:
        self.piorx = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.piorx.clear()
        self.msg_detected = False
        self.msg_estTstart = ticks_ms() #Estimated start time
        return

    def pulses_getnonblock(self): #Get raw message (if exists) using non-blocking method
        buf = self.piorx
        N = len(buf)
        if N < 2: #No signal yet
            return None
        if not self.msg_detected:
            self.msg_estTstart = ticks_ms() #Hopefully wasn't that long ago.
            self.msg_detected = True

        now = ticks_ms()
        msg_avail = (now - self.msg_estTstart > self.msgmax_ms)
        msg_avail = msg_avail or (buf[N-1] > self.doneT_us)
        if not msg_avail:
            return None

        #TODO: only copy until first doneT_us event??? Right now: assume user calls sufficiently often.
        pulses = array_pulses(buf[i] for i in range(N)) #Quickly copy
        self.reset() #Ready for next message
        return pulses
    
    def msg_read(self): #Non-blocking
        pulses = self.pulses_getnonblock()
        if pulses != None:
            print(pulses)

#Last line