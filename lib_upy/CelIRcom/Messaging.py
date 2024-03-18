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


#=Special messages
#===============================================================================
IRMSG32_NECRPT = IRMsg32(IRProtocols.NECRPT, 0)

#Last line
