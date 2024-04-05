#CelIRcom/Debug.py: Split out... so we don't have to load code.
#-------------------------------------------------------------------------------
from .Messaging import IRMsg32
from .Protocols import IRProtocols


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
    print(msg)
    if not verbose:
        return
    Nbits = msg.prot.Nbits
    if Nbits > 0:
        fmt = "{:0" + f"{Nbits}" + "b}"
        print("bits: " + fmt.format(msg.bits))
    if msg.prot is IRProtocols.NEC:
        print("Overlaying to see complimentary pattern:")
        _printNECoverlay(msg.bits)
