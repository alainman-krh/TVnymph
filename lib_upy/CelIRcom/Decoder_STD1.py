#CelIRcom/Decoder_STD1.py: Message decoder for messages conforming to "STD1"
#-------------------------------------------------------------------------------
from .Protocols import ptrain_ticks, IRProtocolDef_STD1
from .Protocols import ptrain_pulseio as ptrain_native #Native... for this decoder
from micropython import const

#TODO: Move `ptrain_pulseio` preamble detection to Rx_pulseio. This file should be backend agnostic.

#=Constants
#===============================================================================
MATCH_RELTOL = const(0.2) #20% relative tolerance for identifying start bits as matching
NPULSE_SYMB = const(2) #Algorithm only supports symbols made up of mark-space pulses


#=Helper functions
#===============================================================================
def _pat_validate(pat):
    N = len(pat)
    if 0 == N:
        return ptrain_ticks((1, -1)) #Fill with something
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
        self.tickT = prot.tickT #in usec

        #Compute min/max pulse pattern widths:
        tpat_pre = _pat_validate(prot.pat_pre)
        MATCH_ABS = round(self.tickT*MATCH_RELTOL)
        tickT_min = self.tickT - MATCH_ABS
        self.patTmin_pre = ptrain_native(abs(_ticks)*tickT_min for _ticks in tpat_pre)
        tickT_max = self.tickT + MATCH_ABS
        self.patTmax_pre = ptrain_native(abs(_ticks)*tickT_max for _ticks in tpat_pre)

        self.Nticks_pre = abs(tpat_pre[0]) + abs(tpat_pre[1])
        self.patK_symb = (_pat_validate(prot.pat_bit[0]), _pat_validate(prot.pat_bit[1])) #Symbol (0/1) pattern
        self.patK_post = _pat_validate(prot.pat_post)
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
    def preamble_detect_tickT(self, ptrain_us):
        pre_min = self.patTmin_pre; pre_max = self.patTmax_pre #Local alias
        NOMATCH = (0, 0)
        N = len(ptrain_us)
        i = 0 #Index into ptrain_us[].

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

        #===Extract ACTUAL pulse clock/unit period (tickT) from preamble
        #   (use tickT it to update pulse pattern lenghts):
        tickT = Tpre//self.Nticks_pre #TODO: SPEEDOPT mult+rshift
        istart_msg = i #Where actual message starts
        return (tickT, istart_msg) #Will be non-zero if preamble detected

#-------------------------------------------------------------------------------
    #@micropython.native #TODO
    def msg_decode(self, ptrainK):
        NOMATCH = None
        ptrainKview = memoryview(ptrainK) #Avoids copies
        N = len(ptrainK)
        i = 0

        #==Extract message bits:
        patK_symb = self.patK_symb; Nsymb = len(patK_symb)
        Nleft = self.Nsymbols_msg
        msg = 0
        maxi = N-1 #(cache value) Don't read beyond ptrain_us
        while i < maxi: 
            if Nleft < 1:
                break
            ppat_meas = ptrainKview[i:(i+2)]
            match = False
            for symval in range(Nsymb): #symval: usually represents a single bit
                match = self._match2(patK_symb[symval], ppat_meas)
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
        patK_post = self.patK_post
        ppat_meas = ptrainKview[i:(i+2)]
        match = self._match2(patK_post, ppat_meas)
        if not match:
            return NOMATCH
        return msg

#Last line