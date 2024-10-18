#CelIRcom/Protocols_PLE.py: Pulse-length encoding
#-------------------------------------------------------------------------------
from .Protocols_PDE import IRProtocolDef_PDE as IRProtocolDef_PLE #Use this for now... because implementation "just works".
from .Protocols_PDE import Decoder_PDE as Decoder_PLE #Same.


#=Protocol definitions
#===============================================================================
class IRProtocols:
    #SONY: Technically pulse-length encoding (PLE)... and the preamble is a single pulse
    #...but protocol can actually be represented with IRProtocolDef_PDE
    SONY20 = IRProtocolDef_PLE("Sony20", tickUS=600,
        pre=(4, -1), post=tuple(), _0=(2, -1), _1=(1, -1),
        Nbits=20, f=40_000, duty=1/4, msgintervalMS=45 #Have no clue about interval. Put something reasonable.
        #TMSG<65ms: Pulse train lasts < (5+3*20)*tickUS
    )
    SONY12 = IRProtocolDef_PLE("Sony12", tickUS=600,
        pre=(4, -1), post=tuple(), _0=(2, -1), _1=(1, -1),
        Nbits=12, f=40_000, duty=1/4, msgintervalMS=45
        #TMSG<25ms: Pulse train lasts < (5+3*12)*tickUS
    )


#=Constructors for IR message decoders (Don't auto-build. Allocates memory)
#===============================================================================
def DecoderSony20():
    return Decoder_PLE(IRProtocols.SONY20)
def DecoderSony12():
    return Decoder_PLE(IRProtocols.SONY12)

# Last line