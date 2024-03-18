#CelIRcom/Protocols.py
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
    def __init__(self, Tunit, pre, post, _0, _1, Nbits=32, f=38000, duty=1/4, msginterval_ms=0):
        #msginterval_ms: Minimum time interval between start of repeated messages
        #Default: 32 code bits, 50% duty cycle at 38kHz.
        self.Tunit = Tunit #in usec
        self.pat_pre = array_ticks(pre)
        self.pat_post = array_ticks(post)
        self.pat_bit = (array_ticks(_0), array_ticks(_1))
        self.Nbits = Nbits
        self.f = f
        self.duty_int = round((1<<16)*duty) #Assume 1<<16 means "one" here
        self.msginterval_ms = msginterval_ms

class IRProtocols:
    #NEC WARNING: Protocol appears to expect exactly (-ish) 110ms interval
    #             (start-to-start) for "repeats" to be detected.
    NEC = IRProtocolDef_STD1(Tunit=2250//4, #Regular NEC messages
        pre=(16, -8), post=(1,), _0=(1, -1), _1=(1, -3),
        Nbits=32, f=38000, duty=1/2, msginterval_ms=110
        #Due to complementary nature of signal:
        #TMSG=68ms: Pulse train should always last 121*Tunit
    )
    NECRPT = IRProtocolDef_STD1(Tunit=2250//4, #NEC "Protocol" for special repeat message
        pre=(16, -4), post=(1,), _0=tuple(), _1=tuple(),
        Nbits=0, f=38000, duty=1/4, msginterval_ms=110 #No bits to transmit here
        #TMSG=12ms: Pulse train lasts 21*Tunit
    )

#Last line
