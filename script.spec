# -*- mode: python -*-
a = Analysis(['script.py'],
             pathex=['/Users/jacobkahn/Documents/Programming/Hackathons/PennApps - Hacking/Pickup/pickup-utilities'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='script',
          debug=False,
          strip=None,
          upx=True,
          console=True )
