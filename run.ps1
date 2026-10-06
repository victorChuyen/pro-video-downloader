# Script to run the Video Downloader without console
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
cd $scriptPath

# Kiểm tra thư viện trong .venv
if (Test-Path ".venv\Scripts\pythonw.exe") {
    Start-Process ".venv\Scripts\pythonw.exe" "app.py"
} else {
    Start-Process pythonw.exe "app.py"
}
