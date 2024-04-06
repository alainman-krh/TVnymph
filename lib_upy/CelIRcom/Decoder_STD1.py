#CelIRcom/Decoder_STD1.py: Message decoder for messages conforming to "STD1"
#-------------------------------------------------------------------------------
from .DecoderBase import Decoder_Preamble2, pat2_validate
from .Protocols import ptrain_ticks, IRProtocolDef_STD1
from micropython import const


#=Constants
#===============================================================================
NPULSE_SYMB = const(2) #Algorithm only supports symbols made from a pair (2) of mark-space pulses


#=IR message decoder for protocols adhering to IRProtocolDef_STD1
#===============================================================================
class Decoder_STD1(Decoder_Preamble2):
    """`ptrain_ticks` decoder for protocols adhering to IRProtocolDef_STD1."""
    def __init__(self, prot:IRProtocolDef_STD1):
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

#Last line