@echo off
chcp 65001 >nul
echo === Primix .pmx File Registration ===
echo.
echo This associates .pmx files with Primix.
echo Run this AS ADMINISTRATOR.
echo.
echo Make sure Python is installed.
echo.

set PYTHON_PATH=C:\Python38\pythonw.exe
if not exist "%PYTHON_PATH%" (
    echo Python not found at %PYTHON_PATH%
    echo Trying to find Python...
    for /f "tokens=*" %%i in ('where python 2^>nul') do set PYTHON_PATH=%%i
    if "%PYTHON_PATH%"=="" (
        echo Python not found! Install Python first.
        pause
        exit /b 1
    )
)

echo Python found: %PYTHON_PATH%
echo.

ftype PrimixFile="%PYTHON_PATH%" "%~dp0launcher.pyw" "%%1"
assoc .pmx=PrimixFile

echo Done! .pmx files now open with Primix.
echo Double-click any .pmx file to run.
pause