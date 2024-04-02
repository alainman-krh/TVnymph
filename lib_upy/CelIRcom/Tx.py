#CelIRcom/Tx.py
#-------------------------------------------------------------------------------
from .Protocols import PulseCount_Max, IRProtocols, array_ticks, array_pulses
from adafruit_ticks import ticks_ms
import pulseio


#=PulseTrain: stores pulses in signed ticks
#===============================================================================
class PulseTrain: #Default algorithm: 1 symbol -> 2 pulses
    """Builds up the signal from the provided message as a pulse train"""
    def __init__(self):
        self.buf = array_ticks((0,)*PulseCount_Max.PACKET)
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
        self.tx_start = ticks_ms() #ms
        self.tx_complete = ticks_ms() #ms
        self.pulsebuilder = PulseTrain()

    #Implement interface::
    #---------------------------------------------------------------------------
    def io_refreshcfg(self, prot):
        pass
    #def pulsetrain_build(self, msg):
    #def _pulsetrain_send_immediate(self, ptrain):
    #---------------------------------------------------------------------------

    def pulsetrain_send(self, ptrain):
        self.tx_start = ticks_ms()
        self.tx_complete = self.tx_start
        self._pulsetrain_send_immediate(ptrain)
        self.tx_complete = ticks_ms()
        return ptrain

    def msg_send(self, msg):
        #NOTE: ptrain can be any format most practical for a given implementation
        ptrain = self.pulsetrain_build(msg)
        self.io_refreshcfg(msg.prot) #TODO: track last protocol to avoid reconfig???
        return self.pulsetrain_send(ptrain)

#IRTx_pulseio
#-------------------------------------------------------------------------------
class IRTx_pulseio(AbstractIRTx):
    def __init__(self, pin, prot):
        super().__init__()
        self.io_configure(pin, prot)

    def io_configure(self, pin, prot):
        #pulseio transmitter:
        self.piotx = pulseio.PulseOut(pin, frequency=prot.f, duty_cycle=prot.duty_int16)

    def pulsetrain_build(self, msg):
        #Returns a pulsetrain ready to be transitted
        pulses = self.pulsebuilder.build(msg)
        Tunit = msg.prot.Tunit #in us
        pulses_us = array_pulses(abs(p)*Tunit for p in pulses) #TODO: NOALLOC
        return pulses_us

    def _pulsetrain_send_immediate(self, pulses_us):
        self.piotx.send(pulses_us)

#Last line
