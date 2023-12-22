import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    #"excludes": ["tkinter", "unittest"],
    "packages": ["PyQt5", "tmp", "sys", "os","pynput", 'queue', "Xlib"],
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="Button",
    version="2.0.3",
    description="My Button!",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)