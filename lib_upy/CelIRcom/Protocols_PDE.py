#CelIRcom/Protocols_PDE.py
#-------------------------------------------------------------------------------
from .Protocols import ptrain_ticks, AbstractIRProtocolDef, IRMsg32
from .DecoderBase import Decoder_Preamble2, pat2_validate
from micropython import const

#TODO: DEPRECATE "STD1"


#=Constants
#===============================================================================
NPULSE_SYMB = const(2) #Algorithm only supports symbols made from a pair (2) of mark-space pulses


#=Protocol definitions
#===============================================================================
class IRProtocolDef_PDE(AbstractIRProtocolDef):
    """Pulse distance encoding"""
    def __init__(self, id, tickT, pre, post, _0, _1, Nbits=32, f=38000, duty=1/4, msginterval_ms=0):
        #msginterval_ms: Minimum time interval between start of repeated messages
        #Default: 32 code bits, 50% duty cycle at 38kHz.
        self.id = id
        self.tickT = tickT #in usec
        self.pat_pre = ptrain_ticks(pre)
        self.pat_post = ptrain_ticks(post)
        self.pat_bit = (ptrain_ticks(_0), ptrain_ticks(_1))
        self.Nbits = Nbits
        self.f = f
        self.duty_int16 = round((1<<16)*duty) #Assume 1<<16 means "one" here
        self.msginterval_ms = msginterval_ms

#-------------------------------------------------------------------------------
class IRProtocols:
    #NEC WARNING: Protocol appears to expect exactly (-ish) 110ms interval
    #             (start-to-start) for "repeats" to be detected.
    NEC = IRProtocolDef_PDE("NEC", tickT=1125//2, #Regular NEC messages
        pre=(16, -8), post=(1, -1), _0=(1, -1), _1=(1, -3),
        Nbits=32, f=38000, duty=1/4, msginterval_ms=110
        #Due to complementary nature of signal:
        #TMSG=68ms: Pulse train should always last 121*tickT
    )
    NECRPT = IRProtocolDef_PDE("NEC-RPT", tickT=1125//2, #NEC "Protocol" for special repeat message
        pre=(16, -4), post=(1, -1), _0=tuple(), _1=tuple(),
        Nbits=0, f=38000, duty=1/4, msginterval_ms=110 #No bits to transmit here
        #TMSG=12ms: Pulse train lasts 21*tickT
    )
    #SAMSUNG: Basically NEC, but with shorter preamble.
    SAMSUNG = IRProtocolDef_PDE("Samsung", tickT=1125//2, #Regular NEC messages... almost
        pre=(8, -8), post=(1, -1), _0=(1, -1), _1=(1, -3), #Different start bits
        Nbits=32, f=38000, duty=1/4, msginterval_ms=110
        #Not sure if Samsung respects complementary/redundant pattern
    )

#=Special messages
#-------------------------------------------------------------------------------
IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)


#=IR message decoder for protocols adhering to IRProtocolDef_PDE
#===============================================================================
class Decoder_PDE(Decoder_Preamble2):
    """`ptrainT` decoder for protocols adhering to IRProtocolDef_PDE."""
    def __init__(self, prot:IRProtocolDef_PDE):
        super().__init__(prot) #
        self.patK_symb = (pat2_validate(prot.pat_bit[0]), pat2_validate(prot.pat_bit[1])) #Symbol (0/1) pattern
        self.patK_post = pat2_validate(prot.pat_post)
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


#=Constructors for IR message decoders (Don't auto-build. Allocates memory)
#===============================================================================
def DecoderNEC():
    return Decoder_PDE(IRProtocols.NEC)
def DecoderNECRPT():
    return Decoder_PDE(IRProtocols.NECRPT)
def DecoderSamsung():
    return Decoder_PDE(IRProtocols.SAMSUNG)

#Last line