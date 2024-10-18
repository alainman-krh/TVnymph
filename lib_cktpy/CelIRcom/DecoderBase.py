#CelIRcom/DecoderBase.py: Base definition to IR message decoders
#-------------------------------------------------------------------------------
from .ProtocolsBase import ptrainK_build, AbstractIRProtocolDef
from array import array
from micropython import const


#=Constants
#===============================================================================
#Pre-v9 CircuitPython: const() must be integer?!
MATCH_RELTOL = 0.2 #20% relative tolerance for identifying start bits as matching
NPULSE_SYMB = const(2) #Algorithm only supports symbols made from a pair (2) of mark-space pulses


#=Helper functions
#===============================================================================
def ptrainUS_build(a): #Build array of pulse lengths (us)
    #Using unsigned shorts (matching pulseio lib). Cannot store signed values (exception).
    return array('H', a) #Unsigned short: at least 2 bytes

#-------------------------------------------------------------------------------
def pat2_validate(pat):
    #Check for algorithms that only support symbols made from a pair (2) of mark-space pulses
    N = len(pat)
    if 0 == N: #Special case: 0/1 match on NEC-RPT: technically has nothing... but want to avoid crash
        return ptrainK_build((1, -1)) #Fill with something
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
class AbstractDecoder:
    def __init__(self, prot:AbstractIRProtocolDef):
        self.prot = prot #keep a reference

    #Implement interface:
#-------------------------------------------------------------------------------
    #@abstractmethod #Doesn't exist
    def preamble_detect_tickT(self, ptrainUS):
        pass #Return: (tickUSm, istart_msg)
    def msg_decode(self, ptrainK):
        pass


#=Decoder_Preamble2: Many protocols have a 2-pulse preamble
#===============================================================================
class Decoder_Preamble2(AbstractDecoder):
    """Base class for decoders for protocols using a 2-pulse preamble."""
    def __init__(self, prot:AbstractIRProtocolDef):
        super().__init__(prot)
        tickUS = prot.tickUS #in usec
        MATCH_ABS = round(tickUS*MATCH_RELTOL)

        #Compute/store (cached) min/max pulse pattern widths:
        patK_pre = pat2_validate(prot.pat_pre)
        tickUS_min = tickUS - MATCH_ABS
        self.patUSmin_pre = ptrainUS_build(abs(_ticks)*tickUS_min for _ticks in patK_pre)
        tickUS_max = tickUS + MATCH_ABS
        self.patUSmax_pre = ptrainUS_build(abs(_ticks)*tickUS_max for _ticks in patK_pre)
        self.Nticks_pre = abs(patK_pre[0]) + abs(patK_pre[1])

#-------------------------------------------------------------------------------
    def preamble_detect_tickT(self, ptrainUS):
        pre_min = self.patUSmin_pre; pre_max = self.patUSmax_pre #Local alias
        NOMATCH = (0, 0)
        i = 0 #Index into ptrainUS[].

        #===Detect preamble
        Npre = len(pre_min)
        if len(ptrainUS) < (i+Npre):
            return NOMATCH

        Tpre = 0 #Accumulator: total preamble period
        for j in range(Npre): #index into pre_* arrays
            pi = ptrainUS[i]
            if not (pre_min[j] <= pi <= pre_max[j]):
                return NOMATCH
            Tpre += pi
            i += 1

        #===Extract ACTUAL (measured) pulse clock/unit period from preamble:
        tickUSm = Tpre//self.Nticks_pre #TODO: SPEEDOPT mult+rshift
        istart_msg = i #Where actual message starts
        return (tickUSm, istart_msg) #Will be non-zero if preamble detected