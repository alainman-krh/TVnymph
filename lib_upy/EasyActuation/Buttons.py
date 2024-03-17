#EasyActuation/Buttons.py
#-------------------------------------------------------------------------------
from adafruit_neokey.neokey1x4 import NeoKey1x4
from .Base import ticks_ms
from time import sleep


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

    def __init__(self):
        self.state = BtnState.UP
        self.last_press = ticks_ms()

    #@abstractmethod
    def _scan_raw(self): #Scan for raw button state
        return BtnState.UP #Base class won't do anything at the moment

#Scan for signals (depending on state)
#-------------------------------------------------------------------------------
    def _scan_up(self, stateraw): #Called when BtnState.UP
        if BtnState.DOWN == stateraw:
            self.last_press = ticks_ms()
            self.state = BtnState.DOWN
            return BtnSig.PRESS
        return BtnSig.NONE

    def _scan_down(self, stateraw): #Called when BtnState.DOWN
        if BtnState.DOWN == stateraw:
            return BtnSig.HOLD
        elif BtnState.UP == stateraw:
            self.state = BtnState.UP
            return BtnSig.RELEASE
        return BtnSig.NONE

    def signals_detect(self): #Also updates state (Typically: Only run once per loop)
        stateraw = self._scan_raw()
        if BtnState.DOWN == self.state:
            sig = self._scan_down(stateraw)
        else:
            sig = self._scan_up(stateraw)
        return sig


#=EasyNeoKey
#===============================================================================
class EasyNeoKey(EasyButton):
    def __init__(self, obj, idx):
        super().__init__()
        self.obj = obj
        self.idx = idx

    def _scan_raw(self):
        return BtnState.DOWN if self.obj[self.idx] else BtnState.UP

#Last line
