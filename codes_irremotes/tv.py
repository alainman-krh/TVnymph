#codes_irremotes/tv.py: IR Codes for TVs
#-------------------------------------------------------------------------------
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE

#-------------------------------------------------------------------------------
class MSG_SamsungAU8000: #Namespace (Samsung UN50AU8000FXZC)
    PROT = PDE.IRProtocols.SAMSUNG
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0xE0E09966)
    OFF = IRMsg32(PROT, 0xE0E019E6)
    HDMI1 = IRMsg32(PROT, 0xE0E09768)
    HDMI2 = IRMsg32(PROT, 0xE0E07D82)
    HDMI3 = IRMsg32(PROT, 0xE0E043BC)
    STR_NETFLIX = IRMsg32(PROT, 0xE0E0CF30)
    STR_PRIME = IRMsg32(PROT, 0xE0E02FD0)
    STR_SAMSUNGTV = IRMsg32(PROT, 0xE0E0D629)

#-------------------------------------------------------------------------------
class MSG_LG6090: #Namespace (LG UK6090PUA)
    PROT = PDE.IRProtocols.NEC
    RPT = PDE.IRMSG32_NECRPT #Special repeat message

    ON = IRMsg32(PROT, 0x20DF23DC)
    OFF = IRMsg32(PROT, 0x20DFA35C)
    HOME = IRMsg32(PROT, 0x20DF3EC1)
    MENU_SMART = IRMsg32(PROT, 0x20DF3EC1)
    HDMI1 = IRMsg32(PROT, 0x20DF738C)
    HDMI2 = IRMsg32(PROT, 0x20DF33CC)
    HDMI3 = IRMsg32(PROT, 0x20DF9768)
    TVTUNER = IRMsg32(PROT, 0x20DF6B94)
    STR_NETFLIX = IRMsg32(PROT, 0x20DF6A95)
    STR_AMAZON = IRMsg32(PROT, 0x20DF3AC5)
