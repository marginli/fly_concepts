#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""神經元畫板：產生示範畫面（倒序畫，清單上 MaleCNS 在最前）（三份資料各畫右側 APL）。之後要畫新的神經元用 draw.py（說明見 draw.py 開頭）。"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for ds, note in reversed((("mcns", "右側的 APL，取自 MaleCNS。"),
                 ("fw", "右側的 APL，取自 FlyWire；這份資料在畫面上的左右與另兩份相反。"),
                 ("banc", "右側的 APL，取自 BANC。"))):
    subprocess.run([sys.executable, os.path.join(HERE, "draw.py"), "--ds", ds, "--neurons", "APL", "--side", "R",
                    "--title", "APL（右）", "--id", f"{ds}-apl-r", "--note", note], check=True)
