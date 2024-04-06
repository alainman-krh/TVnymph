#CelIRcom/DecoderBase.py: Base definition to IR message decoders
#-------------------------------------------------------------------------------
from .Protocols import ptrain_ticks, AbstractIRProtocolDef
from array import array
from micropython import const



#=Constants
#===============================================================================
MATCH_RELTOL = const(0.2) #20% relative tolerance for identifying start bits as matching
NPULSE_SYMB = const(2) #Algorithm only supports symbols made from a pair (2) of mark-space pulses


#=Helper functions
#===============================================================================
def ptrain_us(a): #Build array of pulse lengths (us) - unsigned
    #WARNING: Cannot store signed values (exception).
    return array('H', a) #Unsigned short: at least 2 bytes

#-------------------------------------------------------------------------------
def pat2_validate(pat):
    #Check for algorithms that only support symbols made from a pair (2) of mark-space pulses
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


#=Base class for decoders
#===============================================================================
class Decoder_Preamble2():
    """Base class for decoders for protocols using a 2-pulse preamble."""
    def __init__(self, prot:AbstractIRProtocolDef):
        self.prot = prot #keep a reference
        tickT = prot.tickT #in usec
        MATCH_ABS = round(tickT*MATCH_RELTOL)

        #Compute/store min/max pulse pattern widths:
        tpat_pre = pat2_validate(prot.pat_pre)
        tickT_min = tickT - MATCH_ABS
        self.patTmin_pre = ptrain_us(abs(_ticks)*tickT_min for _ticks in tpat_pre)
        tickT_max = tickT + MATCH_ABS
        self.patTmax_pre = ptrain_us(abs(_ticks)*tickT_max for _ticks in tpat_pre)
        self.Nticks_pre = abs(tpat_pre[0]) + abs(tpat_pre[1])

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

    #Interface to be implemented
#-------------------------------------------------------------------------------
    #@abstractmethod #Doesn't exist
    #def msg_decode(self, ptrainK:ptrain_ticks):
