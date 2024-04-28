#CelIRcom/EasyIRRx.py
#-------------------------------------------------------------------------------
from .Timebase import now_ms, ms_elapsed, ms_addwrap, clamp
from .ProtocolsBase import AbstractIRMessage
from .DecoderBase import AbstractDecoder
from .TRxBase import AbstractIRRx


#=EasyRx
#===============================================================================
class EasyRx: #State machine (FSM) helping to schedule outgoing IR messages
    def __init__(self, rx:AbstractIRRx, decoder:AbstractDecoder, decoderRPT:AbstractDecoder=None, msgRPT=None):
        """
        - decoderRPT: In case different from decoder
        - msgRPT: Set to none if protocol just re-sends original message
        """
        self.rx = rx
        self.msgRPT = msgRPT
        prot = decoder.prot
        #Pad-up tolerance on interval (don't ignore repeats due to slight mis-timings):
        self.msgintervalMS = round(prot.msgintervalMS * 1.5)
        declist = [decoder]
        if decoderRPT !=None:
            declist.append(decoderRPT)
        rx.decoders_setactive(declist)

        self.msglast = None
        self.msglast_startMS = now_ms()
        self.pevents_currentstate = self._pevents_idle

#State-dependent (internal) event handlers
#-------------------------------------------------------------------------------
    def _pevents_idle(self, msg:AbstractIRMessage, msg_read_startMS):
        if msg is None:
            return
        elif self.msgRPT == msg:
            return #Not sure what original was. Ignore
        self.msglast = msg
        self.msglast_startMS = msg_read_startMS
        self.pevents_currentstate = self._pevents_held
        self.handle_press(msg)

    def _pevents_held(self, msg:AbstractIRMessage, msg_read_startMS):
        #Receiving IR messages (as if button was pressed/held)
        deltaMS = ms_elapsed(self.msglast_startMS, msg_read_startMS)

        is_repeat = False
        if self.msgRPT != None:
            is_repeat = (msg == self.msgRPT)
        else:
            is_repeat = (msg == self.msglast)

        #Is the signal something invalid?
        sig_invalid = (msg != None) and (not is_repeat)
        release = (deltaMS > self.msgintervalMS) or sig_invalid
        if release:
            msg = self.msglast #Keep reference for handle_release()
            self.msglast = None
            self.pevents_currentstate = self._pevents_idle
            self.handle_release(msg)
            return
        elif msg is None:
            return #No signal. No timeout.

        #We detected a proper repeat message:
        self.msglast_startMS = msg_read_startMS
        self.handle_hold(self.msglast)

#Process button events
#-------------------------------------------------------------------------------
    def process_events(self):
        msg_read_startMS = now_ms() #Proxy for start of message reception
        msg:AbstractIRMessage = self.rx.msg_read() #rx periodically does gc to clean up msg.
        self.pevents_currentstate(msg, msg_read_startMS)

#User-facing event handlers (optionally/application-dependent)
#-------------------------------------------------------------------------------
    #Assuming Rx only deals with 1 protocol: should be fine to only provide msg_bits.
    #Advantage: (Theoretically) wouldn't need to use heap... but would have to use native int type???
    #Not sure if this is a problem.
    def handle_press(self, msg:AbstractIRMessage):
        pass
    def handle_hold(self, msg:AbstractIRMessage):
        pass
    def handle_release(self, msg:AbstractIRMessage):
        pass

#Last line