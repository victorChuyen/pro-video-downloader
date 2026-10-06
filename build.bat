@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Pro Video Downloader - Build Tool
echo ============================================
echo.

REM --- Tim trinh thong dich Python phu hop (uu tien .venv neu co) ---
set PYCMD=
if exist ".venv\Scripts\python.exe" (
    set PYCMD=.venv\Scripts\python.exe
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set PYCMD=python
    ) else (
        where py >nul 2>nul
        if %errorlevel%==0 (
            set PYCMD=py
        )
    )
)

if "%PYCMD%"=="" (
    echo [LOI] Khong tim thay Python. Hay cai Python tu https://python.org
    echo       Nho tick vao o "Add Python to PATH" khi cai dat.
    pause
    exit /b 1
)

echo Dang dung: %PYCMD%
%PYCMD% --version
echo.

echo [1/4] Dang kiem tra / cap nhat thu vien...
%PYCMD% -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [CANH BAO] Khong chay duoc pip install truc tiep, thu tiep tuc voi ban hien tai...
)

echo [2/4] Kiem tra phien ban yt-dlp da cai...
%PYCMD% -c "import yt_dlp; print('  yt-dlp version:', yt_dlp.version.__version__)"

echo [3/4] Dang build file .exe (co the mat 2-4 phut do nhung kem FFmpeg)...
echo.
%PYCMD% -m PyInstaller --noconfirm --clean Pro_VideoDownloader_VictorChuyen.spec
if errorlevel 1 (
    echo.
    echo [LOI] Build that bai. Xem loi phia tren.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   HOAN TAT!
echo   File .exe nam trong thu muc: dist\Pro_VideoDownloader_VictorChuyen.exe
echo ============================================
echo.
pause
