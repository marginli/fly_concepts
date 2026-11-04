#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：纖維版 LPU（A1_fib）三份資料的成果網頁，用 iframe 嵌入。

網頁本身（約 187 MB，含每區全部局部神經元骨架）複製在本條目的 lpu/ 資料夾。
產生步驟（實驗室主機 ~/claude_linux/CMU_research/skeleton/）：
  1. bash run_all.sh 80 fw75 fc75          # 計算（F1 份額 → F4 併區 → F5 A1 管線 → F6 反覆切分 → F7 讀法 A）
  2. cd web && ~/anaconda3/bin/python3 build/export_data.py
  3. ~/anaconda3/bin/python3 build/export_all_ln.py --procs 6
  4. python3 build/inject.py               # 把 build/rules.html、about.html 填進 site/index.html
  5. rsync -a web/site/ <本條目>/lpu/       # 複製進本條目，再在 fly_concepts 跑 ./publish.sh
這支程式不產生任何檔案。"""
print(__doc__)
