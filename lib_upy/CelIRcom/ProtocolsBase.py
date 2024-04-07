#CelIRcom/ProtocolsBase.py
#-------------------------------------------------------------------------------
from micropython import const
from array import array

#Naming convention:
#- tickUS: Tick period in usec
#- patK: pulse pattern in "tick count" (each spanning tickUS)
#- patUS: pulse pattern in usec
#- ptrainK: pulse train (array) in "tick count"
#- ptrainUS: pulse train (array) in usec


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
def ptrainK_build(a): #Build array: # of pulse ticks for a symbol (1 tick lasts 1 tickUS)
    return array('b', a) #Store as byte arrays


#=Abstract definitions
#===============================================================================
class AbstractIRMessage:
    pass

class AbstractIRProtocolDef:
    def __init__(self, id, tickUS):
        self.id = id
        self.tickUS = tickUS 

    #Implement interface:
#-------------------------------------------------------------------------------
    def encode(self, ptrainK, msg:AbstractIRMessage):
        """Fill ptrainK with pulse pattern for transmitting msg (return number of pulses written)."""
        pass


#=Message classes
#===============================================================================
class IRMsg32(AbstractIRMessage):
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
