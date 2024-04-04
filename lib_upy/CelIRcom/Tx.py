#CelIRcom/Tx.py
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, IRProtocols, ptrain_ticks, ptrain_pulseio
from .Timebase import now_ms
import pulseio


#=PulseTrain: stores pulses in signed ticks
#===============================================================================
class PulseTrain: #Default algorithm: 1 symbol -> 2 pulses
    """Builds up the signal from the provided message as a pulse train"""
    def __init__(self):
        self.buf = ptrain_ticks((0,)*PulseCount_Max.PACKET)
        self.buf_reset()

    def buf_reset(self):
        self.buf[0] = 0 #"Last polarity" (first) assumed positive
        self.N = 0 #Assumes element 0 is valid
        return (self.buf, self.N)

    @staticmethod #Provide all arguments on call stack. called often. Probably more efficient.
    def buf_add(buf, N, parr):
        #Add pulse pattern in parr to buf (merge with current pulse if polarity matches)
        for pulse in parr:
            polL = buf[N] >= 0 #Last polarity
            polP = pulse > 0
            if polL == polP:
                buf[N] += pulse
            else:
                N += 1
                buf[N] = pulse
        return N

    def build(self, msg):
        (buf, N) = self.buf_reset() #Also get aliases

        #Add preamble:
        N = self.buf_add(buf, N, msg.prot.pat_pre)

        #Add message bits themselves:
        pat_bit = msg.prot.pat_bit #array for both bits 0 & 1
        Nbits = msg.prot.Nbits; posN = Nbits-1 #Next bit position (MSB to LSB)
        bits = msg.bits #message/code bits
        while posN >= 0:
            bit_i = (bits >> posN) & 0x1
            N = self.buf_add(buf, N, pat_bit[bit_i])
            posN -= 1

        #Add postamble:
        N = self.buf_add(buf, N, msg.prot.pat_post)

        N += 1 #"Accept" final entry
        self.N = N #Update
        pulses = self.buf
        return pulses[0:N]


#=IRTx
#===============================================================================
class AbstractIRTx:
    def __init__(self):
        self.tx_start = now_ms() #ms
        self.tx_complete = now_ms() #ms
        self.pulsebuilder = PulseTrain()

    #Implement interface::
    #---------------------------------------------------------------------------
    def io_refreshcfg(self, prot):
        pass
    #def ptrain_buildnative(self, msg):
    #def _ptrain_sendnative_immediate(self, ptrainNat):
    #---------------------------------------------------------------------------

    def ptrain_sendnative(self, ptrainNat):
        """Send pulse train ()"""
        self.tx_start = now_ms()
        self.tx_complete = self.tx_start
        self._ptrain_sendnative_immediate(ptrainNat)
        self.tx_complete = now_ms()
        return ptrainNat

    def msg_send(self, msg):
        #NOTE: ptrain can be any format most practical for a given implementation
        ptrainNat = self.ptrain_buildnative(msg)
        self.io_refreshcfg(msg.prot) #TODO: track last protocol to avoid reconfig???
        return self.ptrain_sendnative(ptrainNat)

#IRTx_pulseio
#-------------------------------------------------------------------------------
class IRTx_pulseio(AbstractIRTx):
    def __init__(self, pin, prot):
        super().__init__()
        self.io_configure(pin, prot)

    def io_configure(self, pin, prot):
        #pulseio transmitter:
        self.piotx = pulseio.PulseOut(pin, frequency=prot.f, duty_cycle=prot.duty_int16)

    def ptrain_buildnative(self, msg):
        #Returns a pulsetrain ready to be transitted
        pulses = self.pulsebuilder.build(msg)
        tickT = msg.prot.tickT #in us
        pulses_us = ptrain_pulseio(abs(p)*tickT for p in pulses) #TODO: NOALLOC
        return pulses_us

    def _ptrain_sendnative_immediate(self, ptrainNat):
        self.piotx.send(ptrainNat)

#Last line
