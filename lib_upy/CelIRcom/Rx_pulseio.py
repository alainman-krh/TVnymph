#CelIRcom/Rx_pulseio.py: IR receiver for `pulseio` backend
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks, ptrain_pulseio, IRMSG_TMAX_MS
from .Decoder_STD1 import IRProtocolDef_STD1, Decoder_STD1
from .Messaging import IRMsg32
from .Timebase import now_ms, ms_elapsed
from micropython import const
import pulseio
import gc

#TODO: use .readinto()


#=IRRx
#===============================================================================
class IRRx: #Implementation for `pulseio` backend.
    def __init__(self, pin, doneT_ms=20, msgmax_ms=IRMSG_TMAX_MS, autoclear=True):
        #doneT_ms: period of inactivity used to detect end of message transmission.
        #autoclear: auto-clear recieve queue before we ask to read a new message
        #super().__init__()
        doneT_ms = max(10, doneT_ms) #No less than 10ms
        self.doneT_us = doneT_ms * 1_000 #Code needs us: Cache-it!
        #self.doneT_ms = max(1, round((doneT_us+500)//1_000)) #Some code needs ms: Cache-it!
        self.msgmax_ms = msgmax_ms
        self.autoclear = autoclear
        self.ptrainK_buf = ptrain_ticks(range(PulseCount_Max.PACKET+5))
        self.io_configure(pin, maxlen=120)
        self.reset()

#-------------------------------------------------------------------------------
    def io_configure(self, pin, maxlen):
        #pulseio receiver:
        self.piorx = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=False)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.piorx.clear()
        self.msg_detected = False
        self.msg_estTstart = now_ms() #Estimated start time

#-------------------------------------------------------------------------------
    def _decoder_build(self, prot):
        T = prot.__class__
        #TODO: Figure out a way to do this without importing all protocols (save space)
        if T is IRProtocolDef_STD1:
            return Decoder_STD1(prot)
        raise Exception(f"Protocol not supported: {T}")

    def protocols_setactive(self, prot_list):
        self.decoders = tuple(self._decoder_build(prot) for prot in prot_list)

#-------------------------------------------------------------------------------
    def ptrain_readnonblock(self): #Get raw pulsetrain (if exists) using non-blocking method
        buf = self.piorx
        N = len(buf)
        if N < 2: #Need to look past first period of "nothingness" to see signal
            return None #No signal yet

        now = now_ms()
        if not self.msg_detected:
            self.msg_estTstart = now #Hopefully wasn't that long ago.
            self.msg_detected = True

        msg_avail = (ms_elapsed(self.msg_estTstart, now) > self.msgmax_ms)
        msg_avail = msg_avail or (buf[N-1] > self.doneT_us)
        if not msg_avail:
            return None
       
        #TODO: only copy until first doneT_us event??? Right now: assume user calls sufficiently often.
        ptrain_us = ptrain_pulseio(buf[i] for i in range(N)) #Quickly copy - TODO: NOALLOC
        self.reset() #Ready for next message
        return ptrain_us

#-------------------------------------------------------------------------------
    #@micropython.native #TODO
    def msg_sample(self, ptrain_us, tickTm, istart_msg): #Sample pulsetrain to convert to tickTm count
        MAXPKT = PulseCount_Max.PACKET #Can't recognize as a const
        NOMATCH = None
        N = len(ptrain_us)
        i = istart_msg

        Tleft = tickTm>>1 #centers "sampling circuitry" to half bit period before next pulse

        #==Sample pulsetrain:
        buf = self.ptrainK_buf; ibuf = 0
        sgn = 1 #Assume message starts on positive pulse.
        while i < N:
            if ptrain_us[i] > self.doneT_us:
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

#-------------------------------------------------------------------------------
    def msg_decode(self, decoder:Decoder_STD1, ptrain_us):
        (tickTm, istart_msg) = decoder.preamble_detect_tickT(ptrain_us)
        if tickTm <= 0:
            return None
        ptrainK = self.msg_sample(ptrain_us, tickTm, istart_msg)
        if ptrainK is None:
            return None
        #print("sampled", ptrain_ticks(ptrainK)) #Must build `ptrain_ticks` to print
        msg_bits = decoder.msg_decode(ptrainK)
        if msg_bits is None:
            return None
        msg = IRMsg32(decoder.prot, msg_bits)
        return msg

#-------------------------------------------------------------------------------
    def msg_decode_any(self, ptrain_us):
        for decoder in self.decoders:
            #print(f"Trying decoder {decoder.prot.id}...")
            msg = self.msg_decode(decoder, ptrain_us)
            return msg
        return None

    def msg_read(self): #Non-blocking
        ptrain_us = self.ptrain_readnonblock()
        if ptrain_us is None:
            gc.collect() #Should help
            return None
        #print(ptrain_us)
        msg = self.msg_decode_any(ptrain_us)
        gc.collect() #Should help
        return msg

#Last line