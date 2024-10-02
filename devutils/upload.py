# upload.py: Upload code to CircuitPython board
#-------------------------------------------------------------------------------
from os.path import join as joinpath
from os.path import basename, dirname, abspath
import shutil
_THIS_FILE = abspath(__file__); _THIS_DIR = dirname(_THIS_FILE); _THIS_REPO = dirname(_THIS_DIR)

#User config
#-------------------------------------------------------------------------------
DEST = "E:\\"
#proj = joinpath("demos", "TVnymph_livingroom1")
#proj = joinpath("demos", "TVnymph_livingroom2")
proj = joinpath("demos", "mediaRemote")
#proj = joinpath("demos", "PCnymph_IRRxClick")
#proj = joinpath("demos", "test_IRTx_neokey")
#proj = joinpath("demos", "test_IRRx")
refresh_libs = True

#Copy code
#-------------------------------------------------------------------------------
#TODO: Check to make sure all libs are installed???

#DEST = _THIS_REPO #DEBUG
print(f"Writing to {DEST}...")
if refresh_libs:
	for libname in ("CelIRcom", "CtrlInputWrap"):
		print(f"Synchronizing lib '{libname}'...")
		src = joinpath(_THIS_REPO, "lib_upy", libname)
		dest = joinpath(DEST, "lib", libname)
		#print(src, dest) #DEBUG
		shutil.copytree(src, dest, dirs_exist_ok=True)

print(f"Synchronizing '{proj}'...")
src = joinpath(_THIS_REPO, proj, "main.py")
dest = joinpath(DEST, "main.py")
#print(src, dest) #DEBUG
shutil.copyfile(src, dest)

print("DONE.")

print("\nREMINDER: Use a terminal program to access serial monitor (like putty).")
r"""Example serial monitors
Linux:
- `screen /dev/path/to/device` (must install)
Windows:
- putty (must install)
- VSCode: Serial Monitor plugin (by Microsoft)
  Suggest: Line ending = CR / "terminal mode"
"""
#Last line