#CelIRcom/Protocols.py
#-------------------------------------------------------------------------------
from micropython import const
from array import array
#import pwmio

#Naming convention:
#- patT: pulse pattern in time (typ. us)
#- patK: pulse pattern in "tick count" (each spanning tickT)
#- tickT: Tick period (us)
#- tickTm: Tick period (measured) (us)


#=Constants
#===============================================================================
IRMSG_TMAX_MS = const(100) #Maximum message length in ms.

class PulseCount_Max: #Namespace: Maximum number of pulses (pre-allocate Tx buffers)
    PRE = 2; POST = 2 #Pre/Postamble
    #List supported protocols (typ: #of bits * 2 pulses/symbol)
    #- NEC: 32*2
    MSG = 32*2 #Message bits (set to largest from whichever protocol will have the most).
    PACKET = PRE+POST+MSG


#=Helper functions
#===============================================================================
def ptrain_ticks(a): #Build array: # of pulse ticks for a symbol (1 tick lasts 1 tickT)
    return array('b', a) #Store as byte arrays

#TODO: Move to "pulseio"-specific module/file:
def ptrain_pulseio(a): #Build array of pulse lengths (us)
    #pulseio uses unsigned shorts. Cannot store signed values (exception). Cannot store MAXUSHORT into short either.
    return array('H', a) #Unsigned short: at least 2 bytes


#=Protocol definitions
#===============================================================================
class AbstractIRProtocolDef:
    pass

#Covers most "standard" protocols:
class IRProtocolDef_STD1(AbstractIRProtocolDef):
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

class IRProtocols:
    #NEC WARNING: Protocol appears to expect exactly (-ish) 110ms interval
    #             (start-to-start) for "repeats" to be detected.
    NEC = IRProtocolDef_STD1("NEC", tickT=1125//2, #Regular NEC messages
        pre=(16, -8), post=(1, -1), _0=(1, -1), _1=(1, -3),
        Nbits=32, f=38000, duty=1/4, msginterval_ms=110
        #Due to complementary nature of signal:
        #TMSG=68ms: Pulse train should always last 121*tickT
    )
    NECRPT = IRProtocolDef_STD1("NEC-RPT", tickT=1125//2, #NEC "Protocol" for special repeat message
        pre=(16, -4), post=(1, -1), _0=tuple(), _1=tuple(),
        Nbits=0, f=38000, duty=1/4, msginterval_ms=110 #No bits to transmit here
        #TMSG=12ms: Pulse train lasts 21*tickT
    )
    #SAMSUNG: Basically NEC, but with shorter preamble.
    SAMSUNG = IRProtocolDef_STD1("Samsung", tickT=1125//2, #Regular NEC messages... almost
        pre=(8, -8), post=(1, -1), _0=(1, -1), _1=(1, -3), #Different start bits
        Nbits=32, f=38000, duty=1/4, msginterval_ms=110
        #Not sure if Samsung respects complementary/redundant pattern
    )

#Last line
