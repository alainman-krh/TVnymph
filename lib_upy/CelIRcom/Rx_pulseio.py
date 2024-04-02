#CelIRcom/Rx.py
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, IRProtocols, array_ticks, array_pulses, IRMSG_TMAX_MS
from .Protocols import IRProtocolDef_STD1
from .Messaging import IRMsg32
from adafruit_ticks import ticks_ms
from micropython import const
import pulseio
import gc

#Naming convention:
#- patT: pulse pattern in time (typ. us)
#- patU: pulse pattern in base time Unit count (Tunit)


#=Constants
#===============================================================================
MATCH_RELTOL = const(0.2) #20% relative tolerance for identifying start bits as matching
NPULSE_SYMB = const(2) #Algorithm only supports symbols made up of mark-space pulses


#=Helper functions
#===============================================================================
def _pat_validate(pat):
    N = len(pat)
    if 0 == N:
        return array_ticks((1, -1)) #Fill with something
    if N != NPULSE_SYMB:
        raise Exception("Only pos-neg patterns supported")
    for i in range(N):
        isodd = (i & 0x1) != 0
        isneg = pat[i] < 0
        if isodd != isneg:
            raise Exception("Pattern requires even count of alternating pos-neg-...")
    return pat


#=Altered/cached protocol-dependent values optimised for IR message decoding
#===============================================================================
class Decoder_STD1:
    """Cache data for protocols defined by IRProtocolDef_STD1."""
    def __init__(self, prot:IRProtocolDef_STD1):
        self.prot = prot #keep a reference
        self.Tunit = prot.Tunit #in usec

        #Compute min/max pulse pattern widths:
        tpat_pre = _pat_validate(prot.pat_pre)
        MATCH_ABS = round(self.Tunit*MATCH_RELTOL)
        Tunit_min = self.Tunit - MATCH_ABS
        self.patTmin_pre = array_pulses(abs(_ticks)*Tunit_min for _ticks in tpat_pre)
        Tunit_max = self.Tunit + MATCH_ABS
        self.patTmax_pre = array_pulses(abs(_ticks)*Tunit_max for _ticks in tpat_pre)

        self.Nticks_pre = abs(tpat_pre[0]) + abs(tpat_pre[1])
        self.patU_symb = (_pat_validate(prot.pat_bit[0]), _pat_validate(prot.pat_bit[1])) #Symbol (0/1) pattern
        self.patU_post = _pat_validate(prot.pat_post)
        self.Nsymbols_msg = prot.Nbits #Expected # of symbols for a complete message
        #TODO: support msginterval_ms?

#-------------------------------------------------------------------------------
    @staticmethod
    def _match2(ppat_tgt, ppat_meas): #Checks if (2-"pulse") symbols match
        for i in range(NPULSE_SYMB):
            if ppat_meas[i] != ppat_tgt[i]:
                return False
        return True

#-------------------------------------------------------------------------------
    def preamble_detect_Tunit(self, ptrain_us):
        pre_min = self.patTmin_pre; pre_max = self.patTmax_pre #Local alias
        NOMATCH = (0, 0)
        N = len(ptrain_us)
        i = 1 #Index into ptrain_us[]. Skip over first entry (="nothingness" before preamble)

        #===Detect preamble
        Npre = len(pre_min)
        if N < (i+Npre):
            return NOMATCH

        Tpre = 0 #Accumulator: total preamble period
        for j in range(Npre): #index into pre_* arrays
            pi = ptrain_us[i]
            if not (pre_min[j] <= pi <= pre_max[j]):
                return NOMATCH
            Tpre += pi
            i += 1

        #===Extract ACTUAL pulse clock/unit period (Tunit) from preamble
        #   (use Tunit it to update pulse pattern lenghts):
        Tunit = Tpre//self.Nticks_pre #TODO: SPEEDOPT mult+rshift
        istart_msg = i #Where actual message starts
        return (Tunit, istart_msg) #Will be non-zero if preamble detected

#-------------------------------------------------------------------------------
    def msg_decode(self, ptrainU):
        NOMATCH = None
        ptrain_mv = memoryview(ptrainU) #Avoids copies
        N = len(ptrainU)
        i = 0

        #==Extract message bits:
        patU_symb = self.patU_symb; Nsymb = len(patU_symb)
        Nleft = self.Nsymbols_msg
        msg = 0
        maxi = N-1 #(cache value) Don't read beyond ptrain_us
        while i < maxi: 
            if Nleft < 1:
                break
            ppat_meas = ptrain_mv[i:(i+2)]
            match = False
            for symval in range(Nsymb): #symval: usually represents a single bit
                match = self._match2(patU_symb[symval], ppat_meas)
                if match:
                    msg = (msg<<1) | symval
                    break
            if not match:
                break #Don't fail NEC-RPT has 0-length message anyhow.
            i += NPULSE_SYMB
            Nleft -= 1
        if Nleft != 0:
            return NOMATCH

        #==Extract postamble:
        patU_post = self.patU_post
        ppat_meas = ptrain_mv[i:(i+2)]
        match = self._match2(patU_post, ppat_meas)
        if not match:
            return NOMATCH
        return msg


#=IRRx
#===============================================================================
#TODO: use .readinto(), and class memoryview, gc.collect()
#IRRx
#-------------------------------------------------------------------------------
class IRRx:
    def __init__(self, pin, doneT_ms=20, msgmax_ms=IRMSG_TMAX_MS, autoclear=True):
        #doneT_ms: period of inactivity used to detect end of message transmission.
        #autoclear: auto-clear recieve queue before we ask to read a new message
        #super().__init__()
        doneT_ms = max(10, doneT_ms) #No less than 10ms
        self.doneT_us = doneT_ms * 1_000 #Code needs us: Cache-it!
        #self.doneT_ms = max(1, round((doneT_us+500)//1_000)) #Some code needs ms: Cache-it!
        self.msgmax_ms = msgmax_ms
        self.autoclear = autoclear
        self.read_last = ticks_ms()
        self.ptrainT_buf = array_ticks(range(PulseCount_Max.PACKET+5))
        self.io_configure(pin, maxlen=120)
        self.reset()

#-------------------------------------------------------------------------------
    def io_configure(self, pin, maxlen):
        #pulseio receiver:
        self.piorx = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.piorx.clear()
        self.msg_detected = False
        self.msg_estTstart = ticks_ms() #Estimated start time

#-------------------------------------------------------------------------------
    def _decoder_build(self, prot):
        T = prot.__class__
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
        if not self.msg_detected:
            self.msg_estTstart = ticks_ms() #Hopefully wasn't that long ago.
            self.msg_detected = True

        now = ticks_ms()
        msg_avail = (now - self.msg_estTstart > self.msgmax_ms)
        msg_avail = msg_avail or (buf[N-1] > self.doneT_us)
        if not msg_avail:
            return None
       
        #TODO: only copy until first doneT_us event??? Right now: assume user calls sufficiently often.
        ptrain_us = array_pulses(buf[i] for i in range(N)) #Quickly copy - TODO: NOALLOC
        self.reset() #Ready for next message
        return ptrain_us

#-------------------------------------------------------------------------------
    def msg_sample(self, decoder:Decoder_STD1, ptrain_us): #Sample pulsetrain to obtain equivalent in # of measured unitT
        MAXPKT = PulseCount_Max.PACKET #Can't recognize as a const
        NOMATCH = None
        (Tunit, istart_msg) = decoder.preamble_detect_Tunit(ptrain_us)
        if Tunit <= 0:
            return NOMATCH
        N = len(ptrain_us)
        i = istart_msg

        Tleft = Tunit>>1 #centers "sampling circuitry" to half bit period before next pulse

        #==Sample pulsetrain:
        buf = self.ptrainT_buf; ibuf = 0
        ptrain_mv = memoryview(ptrain_us) #Avoids copies
        sgn = 1 #Assume message starts on positive pulse.
        while i < N:
            if ptrain_us[i] > self.doneT_us:
                break
            if ibuf > MAXPKT:
                return NOMATCH

            #Measure pulse duration (# of unit periods) by counting Tunit present
            Tleft += ptrain_us[i]
            Npulse = 0
            while Tleft > Tunit:
                Npulse += 1
                Tleft -= Tunit
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
        ptrainU = self.msg_sample(decoder, ptrain_us)
        if ptrainU is None:
            return None
        ptrainU2 = array_ticks(ptrainU) #Printable
        print("sampled", ptrainU2)
        msg_bits = decoder.msg_decode(ptrainU)
        if msg_bits is None:
            return None
        msg = IRMsg32(decoder.prot, msg_bits)
        return msg

#-------------------------------------------------------------------------------
    def msg_decode_any(self, ptrain_us):
        for decoder in self.decoders:
            print(f"Trying decoder {decoder.prot.id}...")
            msg = self.msg_decode(decoder, ptrain_us)
            if msg != None:
                msg.display_verbose()
                return msg
        return None

    def msg_read(self): #Non-blocking
        ptrain_us = self.ptrain_readnonblock()
        if ptrain_us is None:
            gc.collect() #Should help
            return None
        print(ptrain_us)
        msg = self.msg_decode_any(ptrain_us)
        gc.collect() #Should help

#Last line