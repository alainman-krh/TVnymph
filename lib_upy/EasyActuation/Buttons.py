#EasyActuation/Buttons.py
#-------------------------------------------------------------------------------
from adafruit_neokey.neokey1x4 import NeoKey1x4
from .Base import now_ms, ms_elapsed

#TODO: Debounce


#=Behavioural profiles
#===============================================================================
class Profile:
    def __init__(self, DEBOUNCE_MS=100, LONGPRESS_MS=2000, DBLPRESSMAX_MS=1000):
        #How long something must be held to count as pressed:
        self.DEBOUNCE_MS = DEBOUNCE_MS
        #How long something needs to be held to be considered a "long press":
        self.LONGPRESS_MS = LONGPRESS_MS
        #Maximum time between press events for something to be considered a "double-press":
        self.DBLPRESSMAX_MS = DBLPRESSMAX_MS
        pass

class Profiles:
    DEFAULT = Profile()
    #TODO: Add more profiles!


#=EasyButton_EventHandler
#===============================================================================
class EasyButton_EventHandler:
    """Individual handlers are optionally implemented by user"""
    def handle_press(self, id):
        pass
    def handle_longpress(self, id):
        pass
    def handle_doublepress(self, id):
        pass
    def handle_hold(self, id):
        pass
    def handle_release(self, id):
        pass


#=AbstractEasyButton
#===============================================================================
class AbstractEasyButton:
    def __init__(self, eventhdlr:EasyButton_EventHandler, profile=Profiles.DEFAULT):
        self.eventhdlr = eventhdlr
        self.profile = profile

#Hardware-specific methods
#-------------------------------------------------------------------------------
    #@abstractmethod
    def _physcan_ispressed(self, id): #Scan HW for button state
        return False #Base class won't do anything at the moment
    def process_events(self): #Concrete class should trigger state-machine here
        pass


#=EasyButton_StateMachine
#===============================================================================
class EasyButton_StateMachine: #State machine (FSM) controlling interations with buttons
    def __init__(self, btn:AbstractEasyButton, id=None):
        self.btn = btn
        self.id = id
        self.pevents_currentstate = self._pevents_up
        self.press_start = now_ms()

#State-dependent (internal) event handlers
#-------------------------------------------------------------------------------
    def _pevents_up(self, pressed):
        now = now_ms()
        eventhdlr = self.btn.eventhdlr
        if pressed:
            self.press_start = now
            self.pevents_currentstate = self._pevents_press
            eventhdlr.handle_press(self.id)

    def _pevents_press(self, pressed): #Singlepress
        now = now_ms()
        eventhdlr = self.btn.eventhdlr
        profile = self.btn.profile
        if pressed:
            elapsed = ms_elapsed(self.press_start, now)
            if elapsed >= profile.LONGPRESS_MS:
                self.pevents_currentstate = self._pevents_longpress
                eventhdlr.handle_longpress(self.id)
            eventhdlr.handle_hold(self.id)
        else:
            self.pevents_currentstate = self._pevents_up
            eventhdlr.handle_release(self.id)

    def _pevents_longpress(self, pressed):
        eventhdlr = self.btn.eventhdlr
        if pressed:
            eventhdlr.handle_hold(self.id)
        else:
            self.pevents_currentstate = self._pevents_up
            eventhdlr.handle_release(self.id)

#Process button events
#-------------------------------------------------------------------------------
    def process_events(self):
        """Also updates state (Typically: Only run once per loop)"""
        pressed = self.btn._physcan_ispressed(self.id)
        self.pevents_currentstate(pressed)

    def signals_detect(self): #TODO: Deprecate
        return self.process_events()


#=EasyNeoKey
#===============================================================================
class EasyNeoKey_1x4(AbstractEasyButton):
    def __init__(self, obj:NeoKey1x4, eventhdlr:EasyButton_EventHandler, profile=Profiles.DEFAULT):
        super().__init__(eventhdlr, profile)
        self.statem_list = tuple(EasyButton_StateMachine(self, i) for i in range(4))
        self.obj = obj

    def _physcan_ispressed(self, idx):
        return self.obj[idx]

    def process_events(self, idx=None):
        """Also updates state (Typically: Only run once per loop)"""
        if idx is None:
            for m in self.statem_list:
                m.process_events()
            return
        self.statem_list[idx].process_events()

#Last line
