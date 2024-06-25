import sys
from cx_Freeze import setup, Executable

build_options = {
    'packages': ['PIL', 'pystray', 'requests', 'win32com', 'winshell'],
    'include_files': ['assets'],
    'excludes': ['tkinter'],
}

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

executables = [
    Executable('main.py', base=base, icon='assets/icons/icon.ico', target_name='IPWidget.exe')
]

setup(
    name='ip-widget',
    version='0.3.0',
    description='IP Widget',
    options={'build_exe': build_options},
    executables=executables
)
