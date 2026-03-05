@echo off
:: Siege Scroll Tracker - Auto-elevate and run
net session >nul 2>&1
if %errorlevel% == 0 (
    cd /d "%~dp0"
    python "%~dp0siege_gui.py"
    pause
    exit /b
)
echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\siege_elevate.vbs"
echo UAC.ShellExecute "cmd.exe", "/c cd /d ""%~dp0"" && python ""%~dp0siege_gui.py""", "", "runas", 1 >> "%temp%\siege_elevate.vbs"
"%temp%\siege_elevate.vbs"
del "%temp%\siege_elevate.vbs"
exit /b
