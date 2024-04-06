#CelIRcom/TRxBase.py: Base definitions for IR transmitters/receivers
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, ptrain_ticks
from .Decoder_STD1 import IRProtocolDef_STD1, Decoder_STD1
from .DecoderBase import ptrainUS_build
from .Messaging import IRMsg32
from micropython import const
from array import array
import gc

#TODO: use .readinto()

#Naming convention:
#- tickUSm: Tick period (us) - measured.


#=AbstractIRRx
#===============================================================================
#@micropython.native #TODO
def msg_sample(ptrainK_buf, ptrainUS, tickUSm, istart_msg, doneUS): #Sample pulsetrain to convert to tickUSm count
    NOMATCH = None
    N = len(ptrainUS)
    i = istart_msg

    Tleft = tickUSm>>1 #centers "sampling circuitry" to half bit period before next pulse

    #==Sample pulsetrain:
    buf = ptrainK_buf; ibuf = 0
    sgn = 1 #Assume message starts on positive pulse.
    while i < N:
        if ptrainUS[i] >= doneUS:
            break

        #Measure pulse duration (# of unit periods) by counting # tickUSm present
        Tleft += ptrainUS[i]
        Npulse = 0
        while Tleft > tickUSm:
            Npulse += 1
            Tleft -= tickUSm
        if Npulse < 1:
            return NOMATCH
        if sgn < 0:
            Npulse = -Npulse
        buf[ibuf] = Npulse; ibuf += 1
        i += 1; sgn = -sgn
    if sgn != -1:
        return NOMATCH

    #Add extra item and set to something negative:
    buf[ibuf] = sgn
    Nbuf = ibuf+1
    result = memoryview(buf)[:Nbuf] #Avoids copies
    return result


#=AbstractIRRx
#===============================================================================
class AbstractIRRx:
    def __init__(self):
        doneMS = 20 #(ms) Period of inactivity used to detect end of message transmission.
        self.doneUS = doneMS * 1_000 #Code needs us: Cache-it!
        self.ptrainK_buf = ptrain_ticks(range(PulseCount_Max.PACKET+5)) #NOALLOC
        self.ptrainT_buf = ptrainUS_build(range(PulseCount_Max.PACKET+5)) #NOALLOC
        self.ptrainUS_last = memoryview(self.ptrainT_buf)[:0] #Needs to be updated

#-------------------------------------------------------------------------------
    def ptrainUS_getlast(self):
        """Get a copy of the last detected message"""
        return ptrainUS_build(self.ptrainUS_last) #Must copy to use with print(), etc

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
    def msg_trydecode(self, ptrainUS, decoder:Decoder_STD1):
        (tickUSm, istart_msg) = decoder.preamble_detect_tickT(ptrainUS)
        if tickUSm <= 0:
            return None
        ptrainK = msg_sample(self.ptrainK_buf, ptrainUS, tickUSm, istart_msg, self.doneUS)
        if ptrainK is None:
            return None
        #print("sampled", ptrain_ticks(ptrainK)) #Must build `ptrain_ticks` to print
        msg_bits = decoder.msg_decode(ptrainK)
        if msg_bits is None:
            return None
        msg = IRMsg32(decoder.prot, msg_bits)
        return msg

#-------------------------------------------------------------------------------
    def msg_decode_any(self, ptrainUS):
        for decoder in self.decoders:
            #print(f"Trying decoder {decoder.prot.id}...")
            msg = self.msg_trydecode(ptrainUS, decoder)
            if msg != None:
                gc.collect() #Should help
                return msg
        gc.collect() #Should help
        return None

    def msg_read(self): #Non-blocking
        ptrainUS = self.ptrain_readnonblock()
        if ptrainUS is None:
            return None
        self.ptrainUS_last = memoryview(ptrainUS)
        #print(ptrainUS_build(ptrainUS))
        msg = self.msg_decode_any(ptrainUS)
        return msg

    #Implement interface:
    #---------------------------------------------------------------------------
    #def ptrain_readnonblock(self):