# upload.py: Upload code to CircuitPython board
#-------------------------------------------------------------------------------
from os.path import join as joinpath
from os.path import basename, dirname, abspath
import shutil
_THIS_FILE = abspath(__file__); _THIS_DIR = dirname(_THIS_FILE); _THIS_REPO = dirname(_THIS_DIR)

#User config
#-------------------------------------------------------------------------------
DEST = "E:\\"
proj = joinpath("demos", "test_rxIR")

#Copy code
#-------------------------------------------------------------------------------
#TODO: Check to make sure all libs are installed???

#DEST = _THIS_REPO #DEBUG
print(f"Writing to {DEST}...")
#Blindly uploads every time (might not be great for flash)
for libname in ("CelIRcom", "EasyActuation"):
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

print("\nREMINDER: Use a terminal program to access serial monitor (like ./serialmon.py).")
r"""Example serial monitors
Linux:
- `screen /dev/path/to/device` (must install)
Windows:
- putty (must install)
"""
#Last line