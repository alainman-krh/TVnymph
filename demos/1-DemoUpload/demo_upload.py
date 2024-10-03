# upload.py: Upload code to CircuitPython board
#-------------------------------------------------------------------------------
from UploadTools import UploadProj
from os.path import join as joinpath

#User config
#-------------------------------------------------------------------------------
DEST_DRIVE = "E:\\"
#proj = "TVnymph_livingroom1"
#proj = "TVnymph_livingroom2"
proj = "mediaRemote"
#proj = "PCnymph_IRRxClick"
#proj = "test_IRTx_neokey"
#proj = "test_IRRx"


proj = joinpath("demos", proj)
UploadProj(proj, DEST_DRIVE, refresh_libs=True)

#Last line