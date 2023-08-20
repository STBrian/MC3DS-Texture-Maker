@echo off
title Building 'mc3ds-tm.exe' (pyinstaller)
for /f "delims=" %%a in ('wmic os get localdatetime ^| find "."') do set datetime=%%a
set "datestamp=%datetime:~0,8%"
set "timestamp=%datetime:~8,6%"

echo.
echo. FileName: 'mc3ds-tm.py'.
echo. Build Date/Time: '%DATE%' : '%TIME%'.
echo. Building Application: 'mc3ds-tm.exe' in '%CD%\dist\mc3ds-tm.exe'
echo.
pyinstaller -F --strip --exclude-module numpy --exclude-module opencv --exclude-module cv2 --onefile "mc3ds-tm.py"
exit