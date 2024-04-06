#CelIRcom/TRxBase.py: Base definitions for IR transmitters/receivers
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks
from .Decoder_STD1 import IRProtocolDef_STD1, Decoder_STD1
from .Messaging import IRMsg32
from .Timebase import now_ms, ms_elapsed, ms_addwrap
from micropython import const
import gc

#TODO: use .readinto()


#=AbstractIRTx
#===============================================================================
class AbstractIRTx:
    def __init__(self):
        self.ptrainK_buf = ptrain_ticks(range(PulseCount_Max.PACKET+5)) #NOALLOC

#-------------------------------------------------------------------------------
    def _decoder_build(self, prot):
        T = prot.__class__
        #TODO: Figure out a way to do this without importing all protocols (save space)
        if T is IRProtocolDef_STD1:
            return Decoder_STD1(prot)
        raise Exception(f"Protocol not supported: {T}")

    def protocols_setactive(self, prot_list):
        self.decoders = tuple(self._decoder_build(prot) for prot in prot_list)

#-------------------------------------------------------------------------------
    def msg_trydecode(self, ptrainNat, decoder:Decoder_STD1):
        (tickTm, istart_msg) = decoder.preamble_detect_tickT(ptrainNat)
        if tickTm <= 0:
            return None
        ptrainK = self.msg_sample(ptrainNat, tickTm, istart_msg)
        if ptrainK is None:
            return None
        #print("sampled", ptrain_ticks(ptrainK)) #Must build `ptrain_ticks` to print
        msg_bits = decoder.msg_decode(ptrainK)
        if msg_bits is None:
            return None
        msg = IRMsg32(decoder.prot, msg_bits)
        return msg

#-------------------------------------------------------------------------------
    def msg_decode_any(self, ptrainNat):
        for decoder in self.decoders:
            #print(f"Trying decoder {decoder.prot.id}...")
            msg = self.msg_trydecode(ptrainNat, decoder)
            if msg != None:
                gc.collect() #Should help
                return msg
        gc.collect() #Should help
        return None

    def msg_read(self): #Non-blocking
        ptrainNat = self.ptrain_readnonblock()
        if ptrainNat is None:
            return None
        self.ptrain_native_last = memoryview(ptrainNat)
        #print(ptrain_native(ptrainNat))
        msg = self.msg_decode_any(ptrainNat)
        return msg

    #Implement interface:
    #---------------------------------------------------------------------------
    #def ptrain_readnonblock(self):
    #def msg_sample(self, ptrainNat, tickTm, istart_msg): #Sample pulsetrain to convert to tickTm count