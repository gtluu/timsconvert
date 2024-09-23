# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['TIMSCONVERT_GUI.py'],
    pathex=[],
    binaries=[],
    datas=[
				('TIMSCONVERT_CMD.py', '.'),
				('timsconvert', 'timsconvert'),
				('docs', 'docs'),
				('docsrc', 'docsrc'),
				('imgs', 'imgs'),
				('test', 'test'),
				('C:\\Users\\bass\\.conda\\envs\\timsconvert\\Lib\\site-packages\\TDF-SDK', 'TDF-SDK')
	],
    hiddenimports=[],
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
    name='TIMSCONVERT',
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
    contents_directory='.',
    icon='imgs/timsconvert_icon.ico'
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TIMSCONVERT',
)
