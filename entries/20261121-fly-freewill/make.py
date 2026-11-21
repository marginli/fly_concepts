# -*- coding: utf-8 -*-
"""本條目的產生程式：把簡報 PDF 每頁轉成圖片，並複製簡報、PDF、報告到本資料夾。
簡報本身由 build_deck.py 產生（原檔 ~/claude_yilan/MB/fly_freewill_deck/build.py，需要 deck_lib.py）。
用法：python3 make.py"""
import os, shutil, subprocess, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.expanduser("~/claude_yilan/MB")
for f in ["fly_freewill.pptx", "fly_freewill.pdf", "fly_freewill.docx"]:
    shutil.copy(os.path.join(SRC, f), HERE)
shutil.copy(os.path.join(SRC, "fly_freewill_deck", "build.py"), os.path.join(HERE, "build_deck.py"))
for old in glob.glob(os.path.join(HERE, "slide-*.jpg")):
    os.remove(old)
subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=85", "-r", "80",
                os.path.join(HERE, "fly_freewill.pdf"), os.path.join(HERE, "slide")], check=True)
print(sorted(os.path.basename(p) for p in glob.glob(os.path.join(HERE, "slide-*.jpg"))))
