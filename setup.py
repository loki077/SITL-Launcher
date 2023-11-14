import sys
import os
from cx_Freeze import setup, Executable

PACKAGE_NAME = 'sitl_launcher'
HUMAN_FRIENDLY_NAME = 'SITL-LAUNCHER'

SOURCE_DIR = os.path.abspath(os.path.dirname(__file__))

# unique code so the package can be upgraded as an MSI
upgrade_code = '{D5CD6E19-2545-32C7-A62A-4595B28BCDC3}'

sys.path.append(os.path.join(SOURCE_DIR, PACKAGE_NAME))

assert sys.version_info[0] == 3, 'Python 3 is required'

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": ["unittest"],
    "zip_include_packages": ["os", 
                    "tkinter", 
                    "ttk", 
                    "configparser", 
                    "collections", 
                    "subprocess", 
                    "threading", 
                    "socket", 
                    "time",
                    "requests",
                    "packaging",
                    "webbrowser"],
    "include_files": ["bin", "config", "icons"],  # Add this line
}

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="sitl-launcher",
    version="0.1",
    description='SITL Application Launcher',
    long_description = long_description,        
    long_description_content_type = "text/markdown",
    author='Carbonix Development Team',
    author_email='support@carbonix.com.au',
    url='http://carbonix.com.au',
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py",  
                            shortcut_name=HUMAN_FRIENDLY_NAME,
                            shortcut_dir="DesktopFolder", 
                            base=base)]
)