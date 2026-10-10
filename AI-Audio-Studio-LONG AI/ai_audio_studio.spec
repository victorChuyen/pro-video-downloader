# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [
    ('apps/webapp/static', 'apps/webapp/static'),
    ('apps/webapp/config', 'apps/webapp/config'),
    ('src/vieneu/assets', 'vieneu/assets'),
]
binaries = []
hiddenimports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespans',
    'uvicorn.lifespans.on',
    'sea_g2p',
    'kaldi_native_fbank',
    'soundfile',
    'soxr',
    'onnxruntime',
    'huggingface_hub',
    'tokenizers',
    'librosa',
    'apps.user_voices',
    'webapp.library',
    'vieneu',
    'vieneu.v3turbo',
    'vieneu._v3_turbo_engine',
    'vieneu._v3_turbo_engine.onnx_runtime_lite',
    'vieneu._v3_turbo_engine.speaker.onnx_extractor',
    'starlette.middleware.cors',
    'fastapi.middleware.cors',
]

for pkg in ['sea_g2p', 'kaldi_native_fbank', 'soundfile', 'onnxruntime']:
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

a = Analysis(
    ['apps/webapp/server.py'],
    pathex=['src', 'apps'],
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

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI-Audio-Studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='apps/webapp/static/favicon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI-Audio-Studio',
)
