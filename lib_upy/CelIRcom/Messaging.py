#CelIRcom/Messaging.py
#-------------------------------------------------------------------------------
from .Protocols import IRProtocols #Make available to others
#import pwmio


#=Message classes
#===============================================================================
class IRMsg32:
    def __init__(self, prot, bits):
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


#=Special messages
#===============================================================================
IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)

#Last line
