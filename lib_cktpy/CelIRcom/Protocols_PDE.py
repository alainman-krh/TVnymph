#CelIRcom/Protocols_PDE.py: Pulse-distance encoding
#-------------------------------------------------------------------------------
from .ProtocolsBase import ptrainK_build, AbstractIRProtocolDef, IRMsg32
from .DecoderBase import Decoder_Preamble2, pat2_validate
from micropython import const


#=Constants
#===============================================================================
NPULSE_SYMB = const(2) #Algorithm only supports symbols made from a pair (2) of mark-space pulses


#=Protocol definitions
#===============================================================================
class IRProtocolDef_PDE(AbstractIRProtocolDef):
    """Pulse distance encoding (Default algorithm: 1 symbol -> 2 pulses)"""
    def __init__(self, id, tickUS, pre, post, _0, _1, Nbits=32, f=38_000, duty=1/4, msgintervalMS=0):
        #msgintervalMS: Minimum time interval between start of repeated messages
        #Default: 32 code bits, 25% duty cycle at 38kHz.
        super().__init__(id, tickUS, f, duty)
        self.pat_pre = ptrainK_build(pre)
        self.pat_post = ptrainK_build(post)
        self.pat_bit = (ptrainK_build(_0), ptrainK_build(_1))
        self.Nbits = Nbits
        self.msgintervalMS = msgintervalMS

    #Encoding is simple... we'll do it here (Also more convenient when sending messages):
#-------------------------------------------------------------------------------
    @staticmethod #Provide all arguments on call stack. called often. Probably more efficient.
    def _buf_add(ptrainK, N, parr):
        #Add pulse pattern in parr to ptrainK (merge with current pulse if polarity matches)
        for pulse in parr:
            polL = ptrainK[N] >= 0 #Last polarity
            polP = pulse > 0
            if polL == polP:
                ptrainK[N] += pulse
            else:
                N += 1
                ptrainK[N] = pulse
        return N

    def encode(self, ptrainK, msg):
        """Message->`ptrainK` encoder."""
        buf_add = IRProtocolDef_PDE._buf_add #Alias
        ptrainK[0] = 0 #Output buffer. Initialize "last" value
        N = 0 #Number of bits written to buffer

        #Add preamble:
        N = buf_add(ptrainK, N, self.pat_pre)

        #Add message bits themselves:
        pat_bit = self.pat_bit #array for both bits 0 & 1
        Nbits = self.Nbits; posN = Nbits-1 #Next bit position (MSB to LSB)
        bits = msg.bits #message/code bits
        while posN >= 0:
            bit_i = (bits >> posN) & 0x1
            N = buf_add(ptrainK, N, pat_bit[bit_i])
            posN -= 1

        #Add postamble:
        N = buf_add(ptrainK, N, self.pat_post)
        N += 1 #"Accept" final entry
        return N #How many values are valid


#-------------------------------------------------------------------------------
class IRProtocols:
    #NEC WARNING: Protocol appears to expect exactly (-ish) 110ms interval
    #             (start-to-start) for "repeats" to be detected.
    NEC = IRProtocolDef_PDE("NEC", tickUS=1125//2, #Regular NEC messages
        pre=(16, -8), post=(1, -1), _0=(1, -1), _1=(1, -3),
        Nbits=32, f=38_000, duty=1/4, msgintervalMS=110
        #Due to complementary nature of signal:
        #TMSG=68ms: Pulse train should always last 121*tickUS
    )
    NECRPT = IRProtocolDef_PDE("NEC-RPT", tickUS=1125//2, #NEC "Protocol" for special repeat message
        pre=(16, -4), post=(1, -1), _0=tuple(), _1=tuple(),
        Nbits=0, f=38_000, duty=1/4, msgintervalMS=110 #No bits to transmit here
        #TMSG=12ms: Pulse train lasts 21*tickUS
    )
    #SAMSUNG: Basically NEC, but with shorter preamble.
    SAMSUNG = IRProtocolDef_PDE("Samsung", tickUS=1125//2, #Regular NEC messages... almost
        pre=(8, -8), post=(1, -1), _0=(1, -1), _1=(1, -3), #Different start bits
        Nbits=32, f=38_000, duty=1/4, msgintervalMS=110
        #Not sure if Samsung respects complementary/redundant pattern
    )

#=Special messages
#-------------------------------------------------------------------------------
IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)


#=IR message decoder for protocols adhering to IRProtocolDef_PDE
#===============================================================================
class Decoder_PDE(Decoder_Preamble2):
    """`ptrainK` decoder for protocols adhering to IRProtocolDef_PDE."""
    def __init__(self, prot:IRProtocolDef_PDE):
        super().__init__(prot) #
        self.patK_symb = (pat2_validate(prot.pat_bit[0]), pat2_validate(prot.pat_bit[1])) #Symbol (0/1) pattern
        self.patK_post = prot.pat_post #In case no postamble
        if len(prot.pat_post) > 0: #Assuming there is a postamble
            self.patK_post = pat2_validate(prot.pat_post)
        self.Nsymbols_msg = prot.Nbits #Expected # of symbols for a complete message
        #TODO: support msgintervalMS?

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
        match = True
        patK_post = self.patK_post
        if len(patK_post) > 0: #Some protocols don't have postamble
            ppat_meas = ptrainKview[i:(i+2)]
            match = self._match2(patK_post, ppat_meas)
            i += NPULSE_SYMB
        if (not match) or (i != N): #Should have read EVERYTHING... and matched
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