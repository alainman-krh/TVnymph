#CelIRcom/Encoder_STD1.py: Encoder for messages conforming to "STD1"
#-------------------------------------------------------------------------------
from .Protocols import ptrain_ticks, IRProtocolDef_STD1


#=PulseTrain: stores pulses in signed ticks
#===============================================================================
class Encoder_STD1: #Default algorithm: 1 symbol -> 2 pulses
    """Message->`ptrain_ticks` encoder for protocols adhering to IRProtocolDef_STD1."""
    @staticmethod #Provide all arguments on call stack. called often. Probably more efficient.
    def buf_add(ptrainK, N, parr):
        #Add pulse pattern in parr to ptrainK (merge with current pulse if polarity matches)
        for pulse in parr:
            polL = ptrainK[N] >= 0 #Last polarity
            polP = pulse > 0
            if polL == polP:
                ptrainK[N] += pulse
            else:
                N += 1
                ptrainK[N] = pulse
        return N

#-------------------------------------------------------------------------------
    def build(self, ptrainK, msg):
        ptrainK[0] = 0 #Output buffer. Initialize "last" value
        N = 0 #Number of bits written to buffer

        #Add preamble:
        N = self.buf_add(ptrainK, N, msg.prot.pat_pre)

        #Add message bits themselves:
        pat_bit = msg.prot.pat_bit #array for both bits 0 & 1
        Nbits = msg.prot.Nbits; posN = Nbits-1 #Next bit position (MSB to LSB)
        bits = msg.bits #message/code bits
        while posN >= 0:
            bit_i = (bits >> posN) & 0x1
            N = self.buf_add(ptrainK, N, pat_bit[bit_i])
            posN -= 1

        #Add postamble:
        N = self.buf_add(ptrainK, N, msg.prot.pat_post)
        N += 1 #"Accept" final entry
        return N #How many values are valid
