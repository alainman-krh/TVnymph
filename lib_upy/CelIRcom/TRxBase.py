#CelIRcom/TRxBase.py: Base definitions for IR transmitters/receivers
#-------------------------------------------------------------------------------
from .ProtocolsBase import PulseCount_Max, ptrainK_build, IRMsg32
from .DecoderBase import ptrainUS_build, AbstractDecoder
from .Timebase import now_ms
from micropython import const
import gc

#TODO: use .readinto()
#TODO: Create/re-use TX buffer ptrainUS_build[PulseCount_Max]

#Naming convention:
#- tickUSm: Tick period (us) - measured.


#=msg_sample: mimick sampling hardware counting ticks in each pulse of ptrainUS
#===============================================================================
#@micropython.native #TODO
def msg_sample(ptrainK_buf, ptrainUS, tickUSm, istart_msg, doneUS): #Sample `ptrainUS` - converting to `tickUSm` count
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


#=AbstractIRTx
#===============================================================================
class AbstractIRTx:
    def __init__(self):
        self.tx_start = now_ms() #ms
        self.tx_complete = now_ms() #ms
        self.ptrainK = ptrainK_build((0,)*PulseCount_Max.PACKET) #Buffer

    #---------------------------------------------------------------------------
    def ptrain_sendnative(self, ptrainNat):
        """Send pulse train ()"""
        self.tx_start = now_ms()
        self.tx_complete = self.tx_start
        self._ptrain_sendnative_immediate(ptrainNat)
        self.tx_complete = now_ms()
        return ptrainNat

    def msg_send(self, msg:IRMsg32):
        #NOTE: ptrain can be any format most practical for a given implementation
        N = msg.prot.encode(self.ptrainK, msg)
        ptrainK = memoryview(self.ptrainK)[:N]
        ptrainNat = self.ptrain_buildnative(ptrainK, msg.prot.tickT)
        return self.ptrain_sendnative(ptrainNat)

    #Implement interface:
    #---------------------------------------------------------------------------
    #def ptrain_buildnative(self, ptrainK, tickT):
    #def _ptrain_sendnative_immediate(self, ptrainNat):


#=AbstractIRRx
#===============================================================================
class AbstractIRRx:
    def __init__(self):
        doneMS = 20 #(ms) Period of inactivity used to detect end of message transmission.
        self.doneUS = doneMS * 1_000 #Code needs us: Cache-it!
        self.ptrainK_buf = ptrainK_build(range(PulseCount_Max.PACKET+5)) #NOALLOC
        self.ptrainT_buf = ptrainUS_build(range(PulseCount_Max.PACKET+5)) #NOALLOC
        self.ptrainUS_last = memoryview(self.ptrainT_buf)[:0] #Needs to be updated

#-------------------------------------------------------------------------------
    def ptrainUS_getlast(self):
        """Get a copy of the last detected message"""
        return ptrainUS_build(self.ptrainUS_last) #Must copy to use with print(), etc

#-------------------------------------------------------------------------------
    def decoders_setactive(self, decoder_list):
        for d in decoder_list:
            if not issubclass(d.__class__, AbstractDecoder):
                raise Exception(f"Error in `decoder_list`: `{d}` not a ::AbstractDecoder.")
        self.decoders = decoder_list

#-------------------------------------------------------------------------------
    def msg_trydecode(self, ptrainUS, decoder:AbstractDecoder):
        (tickUSm, istart_msg) = decoder.preamble_detect_tickT(ptrainUS)
        if tickUSm <= 0:
            return None
        ptrainK = msg_sample(self.ptrainK_buf, ptrainUS, tickUSm, istart_msg, self.doneUS)
        if ptrainK is None:
            return None
        #print("sampled", ptrainK_build(ptrainK)) #Must make new object (copy) to print
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
        self.ptrainUS_last = memoryview(self.ptrainT_buf)[:0]
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