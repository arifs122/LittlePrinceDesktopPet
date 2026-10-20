@echo off
rem Kucuk Prens - derleme betigi
rem Kullanim: build.bat [classic / ai / all]
rem   build.bat           -> iki surum birden
rem   build.bat classic   -> dist\LittlePrince.exe   (AI'siz)
rem   build.bat ai        -> dist\LittlePrinceAI.exe (AI'li)
cd /d "%~dp0"
python "%~dp0build.py" %*
if errorlevel 1 exit /b 1
