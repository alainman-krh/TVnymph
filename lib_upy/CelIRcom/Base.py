#CelIRcom/Base.py
#-------------------------------------------------------------------------------
from array import array
#import pwmio

#NOTE: Trying to keep identifiers/variable names shorter. Apparently it matters for space/speed?.


#=Helper functions
#===============================================================================
def array_ticks(a): #Build array: # of pulse ticks for a symbol (1 tick lasts 1 Tunit)
    return array('b', a)


#=Protocol definitions
#===============================================================================
class AbstractIRProtocolDef:
    pass

#Covers most "standard" protocols:
class IRProtocolDef_STD1(AbstractIRProtocolDef):
    def __init__(self, Tunit, pre, post, _0, _1, Nbits=32, f=38000, duty=1/4):
        #Default: 32 code bits, 50% duty cycle at 38kHz.
        self.Tunit = Tunit #in usec
        self.pat_pre = array_ticks(pre)
        self.pat_post = array_ticks(post)
        self.pat_bit = (array_ticks(_0), array_ticks(_1))
        self.Nbits = Nbits
        self.f = f
        self.duty_int = round((1<<16)*duty) #Assume 1<<16 means "one" here

class IRProtocols:
    NEC = IRProtocolDef_STD1(Tunit=2250//4,
        pre=(16, -8), post=(1,), _0=(1, -1), _1=(1, -3),
        Nbits=32, f=38000, duty=1/2
        #Due to complementary nature of signal:
        #- Pulse train should always last 121*Tunit (aprox 68ms)
    )
    #"Protocol" for special repeat packet
    NECRPT = IRProtocolDef_STD1(Tunit=2250//4,
        pre=(16, -4), post=(1,), _0=tuple(), _1=tuple(),
        Nbits=0, f=38000, duty=1/4 #No bits to transmit here
        #- Pulse train lasts 21*Tunit (aprox 12ms)
    )

#-------------------------------------------------------------------------------
class IRMsg32:
    def __init__(self, prot, bits):
        self.prot = prot
        self.bits = bits #message/code bits

IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)

#Last line