#CelIRcom/Timebase.py
#-------------------------------------------------------------------------------
from supervisor import ticks_ms as now_ms
from micropython import const

#- `now_ms` should be sufficient for most human-scale interactions.
#- Use `time.monotonic_ns()` for high-precision measurements instead.


_TICKS_WRAP = const(1<<29)
_TICKS_MASK = const(_TICKS_WRAP-1)
_TICKS_HALFWRAP = const(_TICKS_WRAP//2)

#-------------------------------------------------------------------------------
#Adapted from `ticks_diff` (https://docs.circuitpython.org/en/latest/shared-bindings/supervisor/index.html#supervisor.ticks_ms)
def ticksms_delta(t1, t0): #Notice subtracting 2nd arg.
    """Compute the signed difference between two ticks_ms() values given # counter bits."""
    diff = (t1 - t0) & _TICKS_MASK
    diff = ((diff + _TICKS_HALFWRAP) & _TICKS_MASK) - _TICKS_HALFWRAP
    return diff

#-------------------------------------------------------------------------------
def ticksms_elapsed(t0, t1): #Notice t0 (ref) is first.
    """Always positive"""
    return (t1 - t0) & _TICKS_MASK