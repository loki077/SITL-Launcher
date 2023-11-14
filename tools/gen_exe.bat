del "SITL Launcher.zip"
pyinstaller --onefile --windowed main.py
copy dist\main.exe "SITL Launcher.exe"

rem Create zip file of the exe, config.ini, the ArduPlane exes and dlls, all
rem default.param files under the bin directory, and all lua scripts
7z a -tzip "SITL Launcher.zip" "SITL Launcher.exe" config\config.ini bin\*.exe bin\*.dll bin\*\defaults.param bin\*\scripts\*.lua

pause
