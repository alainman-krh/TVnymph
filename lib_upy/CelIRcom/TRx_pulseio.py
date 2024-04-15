#CelIRcom/TRx_pulseio.py: IR receiver for `pulseio` backend
#-------------------------------------------------------------------------------
from .ProtocolsBase import PulseCount_Max, IRMSG_TMAX_MS, AbstractIRProtocolDef
from .DecoderBase import ptrainUS_build
from .Timebase import now_ms, ms_elapsed, ms_addwrap
from .TRxBase import AbstractIRTx, AbstractIRRx
from micropython import const
import pulseio
import gc

#TODO: use .readinto()
#TODO: Create/re-use buffer ptrainUS_build[PulseCount_Max] (NOALLOC)


#=IRTx
#===============================================================================
class IRTx(AbstractIRTx):
    def __init__(self, pin, prot:AbstractIRProtocolDef):
        super().__init__()
        self.io_configure(pin, prot)

    def io_configure(self, pin, prot:AbstractIRProtocolDef):
        #pulseio transmitter:
        self.piotx = pulseio.PulseOut(pin, frequency=prot.f, duty_cycle=prot.duty_int16)

    def ptrain_buildnative(self, ptrainK, tickUS):
        #Convert ptrainK to a format usable by `PulseOut`:
        return ptrainUS_build(abs(p)*tickUS for p in ptrainK) #TODO: NOALLOC

    def _ptrain_sendnative_immediate(self, ptrainNat):
        self.piotx.send(ptrainNat)


#=IRRx
#===============================================================================
class IRRx(AbstractIRRx): #Implementation for `pulseio` backend.
    def __init__(self, pin):
        super().__init__()
        self.msgmaxMS = IRMSG_TMAX_MS #Used as timeout to process whatever is in buffer
        self.io_configure(pin, maxlen=PulseCount_Max.PACKET*3) #Able to buffer about 3 IR "packets"
        self.reset()

#-------------------------------------------------------------------------------
    def io_configure(self, pin, maxlen):
        #Input buffer talking "directly" (as far as I know) to hardware:
        self.hwbuf = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.hwbuf.clear()
        self.msgstart_detected = False
        self.msg_estTstart = now_ms() #Estimated start time

#-------------------------------------------------------------------------------
    def _hwbuf_popnext(self):
        #Assumption: We have detected a full message exists... or timeout.
        bufin = self.hwbuf
        bufout = self.ptrainUS_buf
        N = len(self.ptrainUS_buf) - 1 #Don't go over... keep 1 to add fake ending (space-"pulse")
        doneUS = self.doneUS #Cache-it
        i = 0
        while i < N:
            if len(bufin) < 1: #Always check... in case there are threading issues
                break
            pulse_len = bufin.popleft()
            bufout[i] = pulse_len
            i += 1
            if (pulse_len > doneUS):
                i -= 1
                if i > 0: #Ok. Found an actual message
                    break
        #endwhile
        if (i & 0x1) > 0: #If odd number of pulses found
            bufout[i] = doneUS #Need trailing "space" to properly decode signals
            i += 1

        if len(bufin) < 1:
            #Don't fully self.reset()... in case pulseio "thread" added a pulse since checked len().
            self.msg_estTstart = now_ms()
            self.msgstart_detected = False
        else:
            #Can't really figure out when the "next" message really started (timers saturate)
            #... so let's assume it starts now (We mostly want to avoid keeping stale data in buffers)
            self.msg_estTstart = now_ms()
            self.msgstart_detected = True
        return memoryview(bufout)[:i]

#-------------------------------------------------------------------------------
    def ptrain_readnonblock(self): #Get raw pulsetrain (if exists) using non-blocking method
        buf = self.hwbuf
        N = len(buf)
        if N < 2: #Need to look past first period of "nothingness" to see signal
            return None #No signal yet

        now = now_ms()
        if not self.msgstart_detected:
            self.msg_estTstart = now #Hopefully wasn't that long ago.
            self.msgstart_detected = True

        msg_avail = (ms_elapsed(self.msg_estTstart, now) > self.msgmaxMS)
        msg_avail = msg_avail or (buf[N-1] >= self.doneUS)
        if not msg_avail:
            return None
       
        #TODO: only copy until first doneUS event??? Right now: assume user calls sufficiently often.
        ptrain_us = self._hwbuf_popnext()
        #ptrain_us = ptrainUS_build(buf[i] for i in range(N)) #Quickly copy - TODO: NOALLOC
        #self.reset() #Ready for next message
        gc.collect() #Should help
        return ptrain_us

#Last line