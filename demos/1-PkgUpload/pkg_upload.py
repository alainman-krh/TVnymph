#pkg_upload.py: Upload project code to CircuitPython board
#-------------------------------------------------------------------------------
from UploadTools import UploadPkg
from os.path import join as joinpath
import os

#User config
#-------------------------------------------------------------------------------
DEST_DRIVE = "E:\\"
#Update/activate to automatically install from Circuit Python library "bundle":
#os.environ["LIBPATH_CPYBUNDLE"] = r"C:\path\to\adafruit-circuitpython-bundle-9.x-mpy\lib"

#pkg = "TVnymph_livingroom1"
#pkg = "TVnymph_livingroom2"
pkg = "MediaRemote_RP2040" #Generates keyboard media key presses (vol/mute, play/ff/rew, etc)
#pkg = "PCnymph_IRRxClick" #Relays IR signals to the "PCnymph" software (currently: mediacontrol_applet in AVglue project)
#pkg = "test_IRTx_neokey" #Send out volume +/- over `NeoKey1x4` ()
#pkg = "test_IRRx"
UploadPkg(pkg, DEST_DRIVE, refresh_libs=True)

#Last line