#CelIRcom/Tx.py
#-------------------------------------------------------------------------------
from .Base import IRProtocols, array_ticks
from array import array
import pulseio


#=PulseCount_Max
#===============================================================================
class PulseCount_Max: #Namespace: Maximum number of pulses (pre-allocate Tx buffers)
    PRE = 2; POST = 2 #Pre/Postamble
    #List supported protocols (typ: #of bits * 2 pulses/bit)
    #- NEC: 32*2
    MSG = 32*2 #Message bits (set to largest from whichever protocol will have the most).
    PACKET = PRE+POST+MSG
#NOTE: Here: an individual "pulse" is defined as a continous series of either
#"marks" or "spaces" - as opposed to a signal that goes low-high-low (definition
#used in the signal analysis formalism).


#=Helper functions
#===============================================================================
def array_pulses(a): #Build array of pulse lengths (us)
    return array('H', a)


#=PulseTrain
#===============================================================================
class PulseTrain: #Default algorithm: 1 bit -> 2 pulses
    #Builds up the signal from the provided message as a pulse train
    def __init__(self):
        self.buf = array_ticks((0,)*PulseCount_Max.PACKET)
        self.buf_reset()

    def buf_reset(self):
        self.buf[0] = 0
        self.N = 0 #Assumes element 0 is valid
        return (self.buf, self.N)

    @staticmethod #Provide all arguments on call stack. called often. Probably more efficient.
    def buf_add(buf, N, parr): #Simplification: assumes 2 pulses
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
        Nbits = msg.prot.Nbits; posN = Nbits-1 #Next bit position
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
class IRTx_pulseio:
    def __init__(self, pin):
        self.pin = pin
        self.pulsebuilder = PulseTrain()
        self.pulse = None #Must .io_configure()         

    def io_configure(self, prot):
        self.pulse=pulseio.PulseOut(self.pin, frequency=prot.f, duty_cycle=prot.duty_int)

    def io_refreshcfg(self, prot):
        pass

    def send(self, msg):
        self.io_refreshcfg(msg.prot) #TODO: track last protocol to avoid reconfig???
        pulses = self.pulsebuilder.build(msg) #Only support 32-bit code for now
        Tunit = msg.prot.Tunit #in us
        pulses_us = array_pulses(abs(p)*Tunit for p in pulses)
        self.pulse.send(pulses_us)
        return (pulses, pulses_us)

#Last line