#pkg_upload.py: Upload project code to CircuitPython board
#-------------------------------------------------------------------------------
from UploadTools import UploadProj
from os.path import join as joinpath

#User config
#-------------------------------------------------------------------------------
DEST_DRIVE = "E:\\"
#proj = "TVnymph_livingroom1"
#proj = "TVnymph_livingroom2"
proj = "MediaRemote_RP2040" #Generates keyboard media key presses (vol/mute, play/ff/rew, etc)
#proj = "PCnymph_IRRxClick" #Relays IR signals to the "PCnymph" software (currently: mediacontrol_applet in AVglue project)
#proj = "test_IRTx_neokey" #Send out volume +/- over `NeoKey1x4` ()
#proj = "test_IRRx"

proj = joinpath("demos", proj)
UploadProj(proj, DEST_DRIVE, refresh_libs=True)

#Last line