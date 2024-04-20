#codes_irremotes/rx_audio.py: IR Codes for audio receivers
#-------------------------------------------------------------------------------
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE

#-------------------------------------------------------------------------------
class MSG_YamahaRX475: #Namespace (Yamaha RX-V475)
    PROT = PDE.IRProtocols.NEC
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0x5EA1B847)
    OFF = IRMsg32(PROT, 0x5EA17887)
    HDMI1 = IRMsg32(PROT, 0x5EA1E21C)
    HDMI2 = IRMsg32(PROT, 0x5EA152AC)
    HDMI3 = IRMsg32(PROT, 0x5EA1B24C)
    HDMI4 = IRMsg32(PROT, 0x5EA10AF4)
    AV4 = IRMsg32(PROT, 0x5EA13AC4)
    AM = IRMsg32(PROT, 0xFE80AA54)
    FM = IRMsg32(PROT, 0xFE801AE4)

#-------------------------------------------------------------------------------
class MSG_PioneerVSX534: #Namespace (Pioneer VSX-534)
    PROT = PDE.IRProtocols.NEC
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0xA55A58A7)
    OFF = IRMsg32(PROT, 0xA55AD827)
    AUX = IRMsg32(PROT, 0xA55AF20D)
