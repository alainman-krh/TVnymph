#CelIRcom/Rx.py
#-------------------------------------------------------------------------------
from .Protocols import IRProtocols, array_ticks, array_pulses, IRMSG_TMAX_MS
from .Protocols import IRProtocolDef_STD1
from adafruit_ticks import ticks_ms
from micropython import const
import pulseio
import gc

#NOTE: ALTERNATE DECODING METHOD:
#WALK THROUGH ALL PULSES STEPPING BY Tunit (measured). CREATE TICK-BASED PULSE
#TRAIN UNTIL HITS LONG PAUSE (doneT_ms). PROTOCOL MATCHING CODE SHOULD BE MORE
#STRAIGHTFORWARD.


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


#=Altered/cached pulse pattern optimized for IR message decoding
#===============================================================================
class PulsePatCache:
    """Cache of UPDATABLE pulse width (us) patterns (don't have to constantly rebuild array)"""
    def __init__(self):
        self.p = array_pulses(tuple(range(NPULSE_SYMB))) #0-terminated
    
    def update(self, Tunit, tick_pat):
        for i in range(NPULSE_SYMB):
            self.p[i] = abs(tick_pat[i]) * Tunit


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
        print(tpat_pre)
        self.ppatmin_pre = array_pulses(abs(_ticks)*Tunit_min for _ticks in tpat_pre)
        Tunit_max = self.Tunit + MATCH_ABS
        self.ppatmax_pre = array_pulses(abs(_ticks)*Tunit_max for _ticks in tpat_pre)
        print(Tunit_min, self.Tunit, Tunit_max)

        self.Nticks_pre = abs(tpat_pre[0]) + abs(tpat_pre[1])
        self.tpat_symb = (_pat_validate(prot.pat_bit[0]), _pat_validate(prot.pat_bit[1])) #Symbol (0/1) pattern
        self.tpat_post = _pat_validate(prot.pat_post)
        self.Nsymbols_msg = prot.Nbits #Expected # of symbols for a complete message
        #TODO: support msginterval_ms?

        #Pulse patterns (us) instead of tick pattern
        self.ppat_symb = (PulsePatCache(), PulsePatCache())
        self.ppat_post = PulsePatCache()

#-------------------------------------------------------------------------------
    @staticmethod
    def _match2(Tunit, ppat_tgt, Tleft, ppat_meas): #Match 2 "pulses"
        #Matching algorithm tries to mimick hardware sampling periodically @ Tunit
        for i in range(NPULSE_SYMB):
            Tfirst = Tunit - Tleft #First sample of pulse is 1*Tunit later
            if Tfirst < 0: #First sample happens BEFORE desired pulse transition
                return (False, 0) #No match
            #Tleft: before next transition (samples does not match target)
            Tleft = Tfirst + ppat_meas[i] - ppat_tgt[i]
            if Tleft < 0: #Last sample happens AFTER pulse transitions again
                return (False, 0) #No match
        return (True, Tleft)

#-------------------------------------------------------------------------------
    def preamble_detect(self, ptrain_us):
        return #TODO: split out this code

#-------------------------------------------------------------------------------
    def msg_decode(self, ptrain_us):
        pre_min = self.ppatmin_pre; pre_max = self.ppatmax_pre #Local alias
        N = len(ptrain_us)
        i = 1 #Index into ptrain_us[]. Skip over first entry (="nothingness" before preamble)

        #===Detect preamble
        Npre = len(pre_min)
        if N < (i+Npre):
            return False #NOMATCH

        Tpre = 0 #Accumulator: total preamble period
        for j in range(Npre): #index into pre_* arrays
            pi = ptrain_us[i]
            if not (pre_min[j] <= pi <= pre_max[j]):
                return False #NOMATCH
            Tpre += pi
            i += 1

        #===Extract ACTUAL pulse clock/unit period (Tunit) from preamble
        #   (use Tunit it to update pulse pattern lenghts):
        Tunit = Tpre / self.Nticks_pre #TODO: SPEEDOPT mult+rshift
        self.ppat_symb[0].update(Tunit, self.tpat_symb[0])
        self.ppat_symb[1].update(Tunit, self.tpat_symb[1])
        self.ppat_post.update(Tunit, self.tpat_post)
        print(Tunit)

        Tleft = Tunit>>1 #centers "sampling circuitry" of _match2() code

        #==Extract message bits:
        ppat_symb = self.ppat_symb; Nsymb = len(ppat_symb)
        Nleft = self.Nsymbols_msg
        msg = 0; match = True
        maxi = N-1 #(cache value) Don't read beyond ptrain_us
        ptrain_mv = memoryview(ptrain_us) #Avoids copies
        while i < maxi: 
            if Nleft < 1:
                break
            ppat_meas = ptrain_mv[i:(i+2)]
            for bit in range(Nsymb):
                (match, Tleft) = self._match2(Tunit, ppat_symb[bit], Tleft, ppat_meas)
                if match:
                    msg = (msg<<1) & bit
                    break
            if not match:
                break #Don't fail NEC-RPT has 0-length message anyhow.
            i += NPULSE_SYMB
            Nleft -= 1
        if Nleft != 0:
            return False #NOMATCH

        #==Extract postamble:
        ppat_post = self.ppat_post; Nsymb = len(ppat_post)
        (match, Tleft) = self._match2(Tunit, ppat_symb[j], Tleft, ppat_meas)
        if not match:
            return False #NOMATCH
        return msg


#=IRRx
#===============================================================================
#TODO: use .readinto(), and class memoryview, gc.collect()
#IRRx
#-------------------------------------------------------------------------------
class IRRx:
    def __init__(self, pin, doneT_ms=10, msgmax_ms=IRMSG_TMAX_MS, autoclear=True):
        #doneT_ms: period of inactivity used to detect end of message transmission.
        #autoclear: auto-clear recieve queue before we ask to read a new message
        #super().__init__()
        doneT_ms = max(10, doneT_ms) #No less than 10ms
        self.doneT_us = doneT_ms * 1_000 #Code needs us: Cache-it!
        #self.doneT_ms = max(1, round((doneT_us+500)//1_000)) #Some code needs ms: Cache-it!
        self.msgmax_ms = msgmax_ms
        self.autoclear = autoclear
        self.read_last = ticks_ms()
        self.io_configure(pin, maxlen=120)
        self.reset()

    def io_configure(self, pin, maxlen):
        #pulseio receiver:
        self.piorx = pulseio.PulseIn(pin, maxlen=maxlen, idle_state=True)

    def _decoder_build(self, prot):
        T = prot.__class__
        if T is IRProtocolDef_STD1:
            return Decoder_STD1(prot)
        raise Exception(f"Protocol not supported: {T}")

    def protocols_setactive(self, prot_list):
        self.decoders = tuple(self._decoder_build(prot) for prot in prot_list)

    def reset(self): #reset recieve queue, ignoring any signal before
        self.piorx.clear()
        self.msg_detected = False
        self.msg_estTstart = ticks_ms() #Estimated start time
        return

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

    def msg_read(self): #Non-blocking
        ptrain_us = self.ptrain_readnonblock()
        if ptrain_us != None:
            print(ptrain_us)
            decoder = self.decoders[1]
            msg_bits = decoder.msg_decode(ptrain_us)
            print(msg_bits)
        gc.collect() #Should help

#Last line