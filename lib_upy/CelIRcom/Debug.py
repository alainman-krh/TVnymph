#CelIRcom/Debug.py: Split out... so we don't have to load code.
#-------------------------------------------------------------------------------
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE


#=Helper functions
#===============================================================================
def _printNECoverlay(msg_bits):
    #Print NEC message bits one on top of the other
    #(They should be complementary)
    for sft in (24, 16, 8, 0):
        val = ((msg_bits>>sft) & 0xFF)
        print(f"{val:08b}")


#=Debugging functions (typ. print)
#===============================================================================
def displaytime_verbose(id, t):
    print(f"{id} (dec): {t}")
    print(f"{id} = 0x{t:X}")

#-------------------------------------------------------------------------------
def display_IRMsg32(msg:IRMsg32, verbose=True):
    print(msg.str_hex())
    if not verbose:
        return
    if msg.prot.Nbits > 0:
        print(msg.str_bin())
    if msg.prot in (PDE.IRProtocols.NEC, PDE.IRProtocols.SAMSUNG):
        print("Overlaying to see complimentary pattern:")
        _printNECoverlay(msg.bits)
