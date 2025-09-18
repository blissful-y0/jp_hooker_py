import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but some modules need help
build_exe_options = {
    "packages": [
        "os",
        "tkinter",
        "win32api",
        "win32con",
        "win32gui",
        "win32process",
        "win32clipboard",
        "psutil",
        "pyperclip",
        "ctypes",
        "threading",
        "queue",
        "json",
        "re"
    ],
    "includes": [
        "tkinter.ttk",
        "tkinter.scrolledtext",
        "tkinter.messagebox",
        "tkinter.filedialog"
    ],
    "excludes": [],
    "include_files": []
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Setup configuration
setup(
    name="Japanese Text Hooker",
    version="1.0",
    description="Japanese text extraction tool for Windows games",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "text_hooker.py",
            base=base,
            target_name="JapaneseTextHooker.exe",
            icon=None
        ),
        Executable(
            "advanced_hooker.py",
            base=base,
            target_name="AdvancedTextHooker.exe",
            icon=None
        )
    ]
)