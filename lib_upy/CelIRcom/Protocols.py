#CelIRcom/Protocols.py
#-------------------------------------------------------------------------------
from micropython import const
from array import array
#import pwmio

#Naming convention:
#- patT: pulse pattern in time (typ. us)
#- patK: pulse pattern in "tick count" (each spanning tickT)
#- tickT: Tick period (us)


#=Constants
#===============================================================================
IRMSG_TMAX_MS = const(100) #Timeout: Maximum message length in ms.

class PulseCount_Max: #Namespace: Maximum number of pulses (pre-allocation of Rx/Tx buffers)
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


#=Abstract definitions
#===============================================================================
class AbstractIRProtocolDef:
    def __init__(self, id, tickT):
        self.id = id
        self.tickT = tickT 

    #Implement interface:
#-------------------------------------------------------------------------------
    def encode(self, ptrainK, msg):
        pass


#=Message classes
#===============================================================================
class IRMsg32:
    """Up-to 32 bit messages"""
    def __init__(self, prot:AbstractIRProtocolDef, bits):
        self.prot = prot
        self.bits = bits #message/code bits
    
    def str_hex(self, prefix="0x") -> str:
        Nbits = self.prot.Nbits
        Nhexdig = (Nbits+3)>>2
        fmt = "{:0" + f"{Nhexdig}" + "X}"
        return f"{self.prot.id} {prefix}" + fmt.format(self.bits)

    def str_bin(self, prefix="0b") -> str:
        Nbits = self.prot.Nbits
        fmt = "{:0" + f"{Nbits}" + "b}"
        return f"{self.prot.id} {prefix}" + fmt.format(self.bits)

    def __str__(self) -> str:
        return self.str_hex()

#Last line
