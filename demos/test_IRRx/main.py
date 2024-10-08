#demos/test_IRRx: Test receiving/decoding IR signals.
#-------------------------------------------------------------------------------
from CelIRcom.TRx_pulseio import IRRx, ptrainUS_build
from CelIRcom.ProtocolsBase import IRMsg32
import CelIRcom.Protocols_PDE as PDE
import CelIRcom.Protocols_PLE as PLE
from CelIRcom.Timebase import now_ms, ms_elapsed
from CelIRcom.Debug import display_IRMsg32, displaytime_verbose
import board


#=Options
#===============================================================================
VERBOSE = True


#=Platform/build-dependent config (Raspberry Pi Pico RP2040)
#===============================================================================
rx_pin = board.GP16


#=Main config
#===============================================================================
rx = IRRx(rx_pin)
rx.decoders_setactive([
    PDE.DecoderNEC(), PDE.DecoderNECRPT(),
    PDE.DecoderSamsung(),
    PLE.DecoderSony12(), PLE.DecoderSony20(),
])


#=Helper functions
#===============================================================================
def display_message_detailed(rx:IRRx, msg:IRMsg32, tmsg):
    ptrain_last = rx.ptrainUS_getlast() #Assumes `msg` was *just* decoded from rx (not a while ago)
    N = len(ptrain_last)
    if msg is None:
        print("\nMessage could not be decoded!")
        if N > 0:
            print(f"Raw message (len={N}):")
            print(ptrain_last)
        return

    print(f"\nIR message detected: {msg.prot.id}")
    displaytime_verbose("---> approx time", tmsg)
    print(f"Raw message (len={N}):")
    print(ptrain_last)
    display_IRMsg32(msg)


#=Test code (sample pulse train w/`pulseio` module)
#===============================================================================
print("=====TESTING WITH SAVED PULSETRAIN=====")
tinit = now_ms()
ptrain_test = ptrainUS_build([9015, 4440, 591, 530, 585, 538, 588, 1659, 593, 529, 616, 507, 619, 504, 622, 500, 615, 508, 618, 1628, 594, 1652, 589, 534, 592, 1654, 587, 1660, 592, 1654, 587, 1660, 592, 1655, 586, 537, 589, 1657, 584, 539, 587, 535, 591, 531, 585, 538, 587, 535, 591, 531, 595, 1652, 589, 533, 593, 1653, 589, 1657, 584, 1662, 590, 1656, 585, 1662, 589, 1657, 585, 40084, 8998, 2212, 587])
msg = rx.msg_decode_any(ptrain_test)
display_message_detailed(rx, msg, tinit)
print("=====TEST DONE=====")


#=Main loop
#===============================================================================
print("\nTVnymph/test_IRRx: ready to receive!")
print("HI0")
while True:
    t0 = now_ms()
    msg:IRMsg32 = rx.msg_read() #Auto prints message when recieves one
    t1 = now_ms()

    #if msg != None: #Acceptable way of detecting successfully decoded message
    if rx.msg_detected(onlydecoded=False):
        if not VERBOSE:
            if msg != None:
                print(msg.str_hex()) #Use simple output
            else:
                print("Message detected - but could not be decoded!")
        else: #Fancy ouptut!
            display_message_detailed(rx, msg, t0)
            print("readtime:", ms_elapsed(t0, t1))
    #endif