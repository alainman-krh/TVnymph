#EasyActuation/Buttons.py
#-------------------------------------------------------------------------------
from adafruit_neokey.neokey1x4 import NeoKey1x4
from .Base import now_ms
from time import sleep


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


#=EasyButton
#===============================================================================
class BtnState:
    UP = 0 #Not pressed
    DOWN = 1 #First pressed

class BtnSig:
    NONE = 0
    PRESS = 1
    HOLD = 2
    RELEASE = 3


#=EasyButton
#===============================================================================
class EasyButton: #State machine (FSM) controlling interations with buttons
    SIG = BtnSig #Alias

    def __init__(self, profile=Profiles.DEFAULT):
        self.state = BtnState.UP
        self.profile = profile
        self.last_press = now_ms()

#Process events: Internal handlers
#-------------------------------------------------------------------------------
    def _process_up(self, pressed): #Called when BtnState.UP
        if pressed:
            self.last_press = now_ms()
            self.state = BtnState.DOWN
            return BtnSig.PRESS
        return BtnSig.NONE

    def _process_down(self, pressed): #Called when BtnState.DOWN
        if pressed:
            return BtnSig.HOLD
        #Otherwise:
        self.state = BtnState.UP
        return BtnSig.RELEASE

#Process events (depends on state)
#-------------------------------------------------------------------------------
    def process_events(self): #Also updates state (Typically: Only run once per loop)
        laststate = self.state #Readability
        pressed = self._physcan_ispressed()
        if BtnState.DOWN == laststate:
            sig = self._process_down(pressed)
        else:
            sig = self._process_up(pressed)
        return sig

    def signals_detect(self): #TODO: Deprecate
        return self.process_events()

#Hardware-specific methods
#-------------------------------------------------------------------------------
    #@abstractmethod
    def _physcan_ispressed(self): #Scan for raw button state
        return False #Base class won't do anything at the moment

#Application-specific event handlers:
#-------------------------------------------------------------------------------
    #TODO


#=EasyNeoKey
#===============================================================================
class EasyNeoKey(EasyButton):
    def __init__(self, obj, idx):
        super().__init__()
        self.obj = obj
        self.idx = idx

    def _physcan_ispressed(self):
        return self.obj[self.idx]

#Last line
