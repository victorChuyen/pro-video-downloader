# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

OPTIONAL_ASSETS = ['coffee.png', 'donate.png', 'real_qr.png', 'icon.ico']

datas = [(f, '.') for f in OPTIONAL_ASSETS if os.path.exists(f)]
datas += [('fonts', 'fonts')]  # font Be Vietnam Pro nhung kem -> chu hien thi dung tren moi may
missing = [f for f in OPTIONAL_ASSETS if not os.path.exists(f)]
if missing:
    print(f"[build] Luu y: khong tim thay {missing} - se build ma khong co cac file nay.")

binaries = []
hiddenimports = []
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('yt_dlp')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('imageio_ffmpeg')  # nhung san FFmpeg -> chay duoc tren moi may, khong can cai rieng
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# Icon file cua .exe
_icon = ['icon.ico'] if os.path.exists('icon.ico') else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Pro_VideoDownloader_VictorChuyen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=['ffmpeg-win-x86_64*.exe'],  # bo qua nen UPX cho FFmpeg
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=_icon,
)
