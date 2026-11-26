#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""條目：FlyWire 四種刺激一起給的交互作用（2026-11-25；FlyWire 783 全腦 LIF 模擬）。
模擬程式：/home/wanju/work/from_desktopTC/multibehavior_20261119/code/mdn_dna02_fw.py（MODE=combo），
說明見同資料夾 multibehavior_plan.md 第 8.47、8.48 節。
模型：Shiu 2024 原始 LIF；嗅葉內部與 2 群細胞的群內連結歸零（共 1.68% 突觸），其他連結原強度。
刺激：LC16 兩側每顆每秒 200 次、LC4 兩側 200、PFL3（軸突送到右側的 12 顆）25、PFL2 兩側 100；開或關共 16 種組合。
每種組合每輪 10 隻；原背景 6 輪（種子 8101–8106）、背景 A（只有嗅覺受器）1 輪、背景 B（18 型搜尋第 41 批）1 輪。
每批撤掉輸入後仍持續放電的果蠅（persist_mask）不列入平均。
讀出：刺激那 1 秒的每秒放電：MDN（4 顆平均）、DNa02 左、右、DNp01（左右平均）。
強度三檔：MODE=dose（×0.5/1/1.5，只有背景＋單獨＋兩兩，67 批），原背景種子 8101–8103 各 10 隻。
用法：python3 make.py → data.json"""
import os, json, glob, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/wanju/work/from_desktopTC/multibehavior_20261119/out"
STIM = ["LC16 兩側", "LC4 兩側", "左 PFL3", "PFL2 兩側"]
ORDER = {"原背景": [f"mdn_combo{s}_pf_fw.json" for s in ["", "_s8102", "_s8103", "_s8104", "_s8105", "_s8106"]],
         "背景A": ["mdn_combo_orn_pf_fw.json"], "背景B": ["mdn_combo_k41_pf_fw.json"]}
RO = {"MDN": ["MDN"], "DNa02L": ["DNa02-L"], "DNa02R": ["DNa02-R"], "DNp01": ["DNp01-L", "DNp01-R"]}
out = {"stim": STIM, "bg": {}}
for bg, files in ORDER.items():
    runs = [{r["stim"]: r for r in json.load(open(os.path.join(SRC, f)))["runs"]} for f in files]
    mean = {k: [] for k in RO}; sem = {k: [] for k in RO}; nex = []
    for bits in itertools.product((0, 1), repeat=4):          # 索引＝LC16×8＋LC4×4＋PFL3×2＋PFL2
        name = "＋".join(s for s, b in zip(STIM, bits) if b) or "只有背景"
        vals = {k: [] for k in RO}; ex = 0
        for R in runs:
            r = R[name]; keep = np.array(r["persist_mask"]) == 0; ex += int((~keep).sum())
            for k, cs in RO.items():
                x = np.mean([np.array(r["cells"][c]["刺激"]) for c in cs], 0)
                vals[k] += list(x[keep])
        for k in RO:
            v = np.array(vals[k]); mean[k].append(round(float(v.mean()), 1)); sem[k].append(round(float(v.std(ddof=1) / np.sqrt(len(v))), 1))
        nex.append(ex)
    out["bg"][bg] = {"mean": mean, "sem": sem, "n_flies": 10 * len(runs), "excluded": nex}
# 11-25 加：強度三檔（MODE=dose，COMBO 強度 ×0.5/1/1.5；只有背景、單獨、兩兩；原背景，種子 8101–8103）
# 鍵＝四種刺激的倍數，例 "0,1.5,0,0.5"；0＝關
DOSE = [{r["stim"]: r for r in json.load(open(os.path.join(SRC, f"mdn_dose_s{s}_fw.json")))["runs"]} for s in (8101, 8102, 8103)]
dose = {}
for name in DOSE[0]:
    m = [0.0] * 4
    if name != "只有背景":
        for part in name.split("＋"):
            st, x = part.rsplit("×", 1); m[STIM.index(st)] = float(x)
    vals = {k: [] for k in RO}; ex = 0
    for R in DOSE:
        r = R[name]; keep = np.array(r["persist_mask"]) == 0; ex += int((~keep).sum())
        for k, cs in RO.items(): vals[k] += list(np.mean([np.array(r["cells"][c]["刺激"]) for c in cs], 0)[keep])
    dose[",".join(f"{v:g}" for v in m)] = {"m": [round(float(np.mean(vals[k])), 1) for k in RO],
                                          "s": [round(float(np.std(vals[k], ddof=1) / np.sqrt(len(vals[k]))), 1) for k in RO], "ex": ex}
out["dose"] = {"keys": list(RO), "n_flies": 10 * len(DOSE), "data": dose}
json.dump(out, open(os.path.join(HERE, "data.json"), "w"), ensure_ascii=False, separators=(",", ":"))
print("data.json", os.path.getsize(os.path.join(HERE, "data.json")), "bytes；排除隻數（原背景）", out["bg"]["原背景"]["excluded"])
