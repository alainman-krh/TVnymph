#CelIRcom/Messaging.py
#-------------------------------------------------------------------------------
from .Protocols import IRProtocols #Make available to others
#import pwmio


#=Helper functions
#===============================================================================
def printNECoverlay(msg_bits):
    #Print NEC message bits one on top of the other
    #(They should be complementary)
    for sft in (24, 16, 8, 0):
        val = ((msg_bits>>sft) & 0xFF)
        print(f"{val:08b}")


#=Message classes
#===============================================================================
class IRMsg32:
    def __init__(self, prot, bits):
        self.prot = prot
        self.bits = bits #message/code bits
    
    def __str__(self) -> str:
        return f"{self.prot.id} {self.bits:08X}"
    
    def display_verbose(self) -> str:
        print(self)
        print(f"{self.bits:032b}")
        printNECoverlay(self.bits)


#=Special messages
#===============================================================================
IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)

#Last line
