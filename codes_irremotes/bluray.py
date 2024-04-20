#codes_irremotes/bluray.py: IR Codes for BluRay players
#-------------------------------------------------------------------------------
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PLE as PLE

#-------------------------------------------------------------------------------
class MSG_SonyBDPS1700: #Namespace (Sony BDP-S1700)
    #Looks like BDP-S1700 expects IR messages to be transmitted 3 times:
    #2nd time: 45 ms after the previous. 3rd time: 125ms after the previous.
    #-"OFF" message appears to be more likely to ignore badly timed sequences.
    PROT = PLE.IRProtocols.SONY20

    ON = IRMsg32(PROT, 0x8B4B8)
    OFF = IRMsg32(PROT, 0x0B4B8)
