#CelIRcom/Rx_pulseio.py: IR receiver for `pulseio` backend
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks, IRMSG_TMAX_MS
from .Protocols import ptrain_pulseio as ptrain_native #Native... for this decoder
from .Timebase import now_ms, ms_elapsed, ms_addwrap
from .TRxBase import AbstractIRRx
from micropython import const
import pulseio
import gc

#TODO: use .readinto()


#=IRRx
#===============================================================================
class IRRx(AbstractIRRx): #Implementation for `pulseio` backend.
    def __init__(self, pin):
        super().__init__()
        doneMS = 20 #(ms) Period of inactivity used to detect end of message transmission.
        self.doneUS = doneMS * 1_000 #Code needs us: Cache-it!
        self.msgmaxMS = IRMSG_TMAX_MS #Used as timeout to process whatever is in buffer
        self.ptrainT_buf = ptrain_native(range(PulseCount_Max.PACKET+5)) #NOALLOC
        self.ptrain_native_last = memoryview(self.ptrainT_buf)[:0] #Needs to be updated
        self.io_configure(pin, maxlen=PulseCount_Max.PACKET*3) #Able to buffer about 3 IR "packets"
        self.reset()

#-------------------------------------------------------------------------------
    def io_configure(self, pin, maxlen):
        #Input buffer talking "directly" (as far as I know) to hardware:
        self.hwbuf = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.hwbuf.clear()
        self.msg_detected = False
        self.msg_estTstart = now_ms() #Estimated start time

    def ptrain_getnative_last(self):
        return ptrain_native(self.ptrain_native_last) #Must copy to use with print(), etc

#-------------------------------------------------------------------------------
    def _hwbuf_popnext(self):
        #Assumption: We have detected a full message exists... or timeout.
        bufin = self.hwbuf
        bufout = self.ptrainT_buf
        N = len(self.ptrainT_buf) - 1 #Don't go over... keep 1 to add fake ending (space-"pulse")
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
            self.msg_detected = False
        else:
            #Can't really figure out when the "next" message really started (timers saturate)
            #... so let's assume it starts now (We mostly want to avoid keeping stale data in buffers)
            self.msg_estTstart = now_ms()
            self.msg_detected = True
        return memoryview(bufout)[:i]

#-------------------------------------------------------------------------------
    def ptrain_readnonblock(self): #Get raw pulsetrain (if exists) using non-blocking method
        buf = self.hwbuf
        N = len(buf)
        if N < 2: #Need to look past first period of "nothingness" to see signal
            return None #No signal yet

        now = now_ms()
        if not self.msg_detected:
            self.msg_estTstart = now #Hopefully wasn't that long ago.
            self.msg_detected = True

        msg_avail = (ms_elapsed(self.msg_estTstart, now) > self.msgmaxMS)
        msg_avail = msg_avail or (buf[N-1] >= self.doneUS)
        if not msg_avail:
            return None
       
        #TODO: only copy until first doneUS event??? Right now: assume user calls sufficiently often.
        ptrain_us = self._hwbuf_popnext()
        #ptrain_us = ptrain_native(buf[i] for i in range(N)) #Quickly copy - TODO: NOALLOC
        #self.reset() #Ready for next message
        gc.collect() #Should help
        return ptrain_us

#-------------------------------------------------------------------------------
    #@micropython.native #TODO
    def msg_sample(self, ptrain_us, tickTm, istart_msg): #Sample pulsetrain to convert to tickTm count
        MAXPKT = PulseCount_Max.PACKET #Can't recognize as a const
        doneUS = self.doneUS #Cache-it
        NOMATCH = None
        N = len(ptrain_us)
        i = istart_msg

        Tleft = tickTm>>1 #centers "sampling circuitry" to half bit period before next pulse

        #==Sample pulsetrain:
        buf = self.ptrainK_buf; ibuf = 0
        sgn = 1 #Assume message starts on positive pulse.
        while i < N:
            if ptrain_us[i] >= doneUS:
                break
            if ibuf > MAXPKT:
                return NOMATCH

            #Measure pulse duration (# of unit periods) by counting # tickTm present
            Tleft += ptrain_us[i]
            Npulse = 0
            while Tleft > tickTm:
                Npulse += 1
                Tleft -= tickTm
            if Npulse < 1:
                return NOMATCH
            if sgn < 0:
                Npulse = -Npulse
            buf[ibuf] = Npulse; ibuf += 1
            i += 1; sgn = -sgn
        if sgn != -1:
            return NOMATCH

        #Add extra item and set to something negative:
        buf[ibuf] = sgn
        Nbuf = ibuf+1
        result = memoryview(buf)[:Nbuf] #Avoids copies
        return result

#Last line