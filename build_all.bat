@echo off
rem Builds both editions:
rem   dist\LittlePrince.exe    (no AI)
rem   dist\LittlePrinceAI.exe  (with AI)
cd /d "%~dp0"

if not exist "app.ico" python tools\make_icon.py

call build_noai.bat
if errorlevel 1 goto :err
call build_ai.bat
if errorlevel 1 goto :err

echo.
echo Both builds are ready in the dist folder.
goto :eof

:err
echo.
echo Build failed.
