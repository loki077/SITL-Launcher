echo off

CHOICE /C YN /M "Are you sure you want to delete all eeprom.bin files?"
IF %ERRORLEVEL% LEQ 1 DEL /Q /F /S "eeprom.bin"
pause
