@echo off
cd /d "F:\AI-Audio-Studio-Windows"
set "PATH=%USERPROFILE%\.local\bin;%USERPROFILE%\.cargo\bin;%PATH%"
set "VIENEU_PORT=8001"
set "VIENEU_MAX_TEXT_CHARS=50000"
start "" cmd /c "ping -n 9 127.0.0.1 ^>nul ^& start http://127.0.0.1:8001"
uv run vieneu-studio
