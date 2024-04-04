#CelIRcom/Debug.py: Split out... so we don't have to load code.
#-------------------------------------------------------------------------------
from .Messaging import IRMsg32
from .Protocols import IRProtocols

def _printNECoverlay(msg_bits):
    #Print NEC message bits one on top of the other
    #(They should be complementary)
    for sft in (24, 16, 8, 0):
        val = ((msg_bits>>sft) & 0xFF)
        print(f"{val:08b}")

def display_IRMsg32(msg:IRMsg32, verbose=True):
    print(msg)
    if not verbose:
        return
    print(f"bits: {msg.bits:032b}")
    if msg.prot is IRProtocols.NEC:
        print("Overlaying to see complimentary pattern:")
        _printNECoverlay(msg.bits)
