#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""神經元畫板：畫一顆或數顆神經元＋相關腦區外形，存成一個「畫面」（views/<id>.json），頁面左側清單會列出來。

用法（在本資料夾）：
  python3 draw.py --ds mcns --neurons APL --side R --title "APL（右）"
  python3 draw.py --ds fw --neurons "KCg-m,MBON01" --side R --max-per-type 3
  python3 draw.py --ds banc --neurons 720575941482622627 --regions "MB_CA_R,MB_PED_R"
參數：
  --ds          mcns（MaleCNS v1.0）／fw（FlyWire v783）／banc（BANC v888）；每次都要指定
  --neurons     逗號分隔；每一項是神經元編號或型別名（型別名比對官方 type／instance）
  --side        R／L；只對型別名有效（編號不篩）
  --max-per-type 每個型別最多畫幾顆（預設 5）
  --show        要畫哪些部分，逗號分隔：fibre（纖維＝骨架）、pre（輸出點）、post（輸入點）；syn＝pre,post。預設 fibre
  --partners    同時畫出和它有突觸相接的神經元（連結對象），逗號分隔：up（上游＝送訊號給它的，它們是突觸前 pre）、
                down（下游＝接收它訊號的，它們是突觸後 post）；也可寫 pre＝up、post＝down、both＝兩者
  --partner-type 只畫型別名符合這個規則運算式的連結對象（例如 "^ORN_" 只畫嗅覺受器神經元）；總數仍列全部
  --syn-partner-type 只畫和這種型別相接的突觸（規則運算式，例如 "^ORN_"）：輸出點只留「接收方至少一顆符合」的，
                輸入點只留「送出方符合」的；表上另列全部數量。資料來源 flyds.synapse_pairs()（mcns 約 15 秒、banc 約 1 分鐘）
  --partner-top 每一邊畫連結數最多的前幾顆（預設 10）；--partner-min 連結數至少多少才畫（預設 5）
                連結數＝兩顆神經元之間的突觸數，來源見 flyds.EDGES；有多顆主角時合併計算、不含主角彼此
  --regions     auto（預設：纖維長度占 ≥ 3% 的腦區，最多 12 個；沒畫纖維時改用畫出的突觸數）／none／逗號分隔的腦區名
  --title       畫面標題；--id 畫面代號（預設由資料集＋神經元組成）；--note 一句說明
  --no-outline  不畫整個神經系統的淡色輪廓
  --remove ID   從清單刪掉一個畫面
腦區名稱：mcns 用官方 v5 腦 80 區；fw 用官方 78 區；banc 用腦 75 區＋腹神經索 26 區。
"""
import argparse, datetime, json, os, re, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "lib"))
import flyds as D                                  # noqa: E402
from flylib import mesh_item, lines_item, points_item, write_scene   # noqa: E402

NEU_COLORS = ["#c0392b", "#1f5fa8", "#1e7a3c", "#8e44ad", "#d35400", "#16a085", "#7f6000", "#c2185b"]
REG_COLORS = ["#e07b39", "#3d7fc1", "#3c9d5d", "#8e7cc3", "#e0a939", "#7cc36a", "#d36b8f", "#5bb5c9",
              "#a0a0a0", "#b5895a", "#9c6fd6", "#6f9c3d"]
MAX_PTS = 150_000          # 全部神經元合計的骨架點數上限（控制檔案大小）
MAX_SYN = 120_000          # 全部神經元合計畫出的突觸點數上限；超過就隨機抽樣（表上列實際數量）
PRE_COLOR, POST_COLOR = "#d62728", "#1f77b4"          # 輸出點紅、輸入點藍（所有畫面固定）
UP_COLOR, DOWN_COLOR = "#2e8b3a", "#e08a00"         # 上游綠、下游橙（避開突觸的紅藍）
MAIN_WITH_PARTNERS = "#222222"                     # 有畫連結對象時，主角用近黑色
SYN_FIBRE_COLORS = ["#555555", "#1e7a3c", "#8e44ad", "#d35400", "#16a085", "#7f6000", "#c2185b", "#5d4037"]
INDEX = os.path.join(HERE, "views.json")


def shade(hexc, k, n):
    """同一型別的第 k 顆：同色、深淺略變。"""
    c = np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], float)
    f = 1.0 if n <= 1 else 0.75 + 0.5 * k / (n - 1)
    c = np.clip(c * f if f <= 1 else c + (255 - c) * (f - 1), 0, 255)
    return "#" + "".join(f"{int(v):02x}" for v in c)


def load_index():
    return json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else []


def save_index(ix):
    json.dump(ix, open(INDEX, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ds", choices=list(D.DS))
    ap.add_argument("--neurons")
    ap.add_argument("--side", choices=["R", "L"])
    ap.add_argument("--max-per-type", type=int, default=5)
    ap.add_argument("--regions", default="auto")
    ap.add_argument("--partners", default="")
    ap.add_argument("--partner-top", type=int, default=10)
    ap.add_argument("--partner-min", type=int, default=5)
    ap.add_argument("--partner-type", default="")
    ap.add_argument("--syn-partner-type", default="")
    ap.add_argument("--show", default="fibre")
    ap.add_argument("--title"); ap.add_argument("--id"); ap.add_argument("--note", default="")
    ap.add_argument("--no-outline", action="store_true")
    ap.add_argument("--remove")
    a = ap.parse_args()

    if a.remove:
        ix = [v for v in load_index() if v["id"] != a.remove]
        save_index(ix)
        p = os.path.join(HERE, "views", f"{a.remove}.json")
        if os.path.exists(p):
            os.remove(p)
        print("已刪除", a.remove); return
    if not (a.ds and a.neurons):
        ap.error("要給 --ds 與 --neurons")

    ds = a.ds
    show = set()
    for x in a.show.split(","):
        x = x.strip()
        show |= {"pre", "post"} if x == "syn" else {x}
    if not show or show - {"fibre", "pre", "post"}:
        ap.error("--show 只能用 fibre、pre、post、syn")
    ends = [e for e in ("pre", "post") if e in show]
    dirs = set()
    for x in a.partners.split(","):
        x = x.strip()
        if x:
            dirs |= {"up", "down"} if x == "both" else {{"pre": "up", "post": "down"}.get(x, x)}
    if dirs - {"up", "down"}:
        ap.error("--partners 只能用 up、down（或 pre、post、both）")
    dirs = [d for d in ("up", "down") if d in dirs]
    # 1. 找神經元：[(型別或編號, [(id, type, side)])]
    groups = []
    for q in [x.strip() for x in a.neurons.split(",") if x.strip()]:
        hits = D.find(ds, q, side=None if q.isdigit() else a.side, limit=a.max_per_type)
        if not hits:
            sys.exit(f"{D.DS[ds]['label']} 找不到 {q}" + (f"（側別 {a.side}）" if a.side else ""))
        hits = [h for h in hits if os.path.exists(D.swc_path(ds, h[0]))] or sys.exit(f"{q}：沒有骨架檔")
        groups.append((q, hits))
    main_ids = [h[0] for _, hits in groups for h in hits]
    # 1b. 連結對象
    part = {}
    for d in dirs:
        allp = D.partners(ds, main_ids, d)
        sel, skipped = [], 0
        for pid, w in allp:
            if len(sel) >= a.partner_top or w < a.partner_min:
                break
            t, sd = D.neuron_info(ds, pid)
            if a.partner_type and not re.search(a.partner_type, t or ""):
                continue
            if not os.path.exists(D.swc_path(ds, pid)):
                skipped += 1
                continue
            sel.append(dict(id=pid, type=t, side=sd, w=w))
        part[d] = dict(n=len(allp), w=sum(w for _, w in allp), sel=sel, no_skel=skipped,
                       min=a.partner_min, filt=a.partner_type)
        if a.partner_type:
            m = [(pid, w) for pid, w in allp if re.search(a.partner_type, D.neuron_info(ds, pid)[0] or "")]
            part[d].update(n_f=len(m), w_f=sum(w for _, w in m))
        print(f"  {'上游' if d == 'up' else '下游'}：共 {len(allp):,} 顆、{part[d]['w']:,} 個連結；畫 {len(sel)} 顆"
              + (f"（{skipped} 顆沒有骨架、略過）" if skipped else ""))
    n_total = sum(len(h) for _, h in groups) + sum(len(p["sel"]) for p in part.values())

    # 2. 骨架與各腦區纖維長度
    names = D.names(ds)
    tot_len, tot_syn = {}, {}
    neu_items, syn_items, rows = [], {"pre": [], "post": []}, []
    palette = SYN_FIBRE_COLORS if ends else NEU_COLORS     # 有畫突觸時，纖維避開紅、藍
    syn = {}
    for q, hits in groups:                                  # 先讀突觸，才知道要不要抽樣
        for nid, _, _ in hits:
            for e in ends:
                syn[(nid, e)] = D.synapses(ds, nid, e)
                if a.syn_partner_type:
                    xyz, oth = D.synapse_pairs(ds, nid, e)
                    keep = np.isin(oth, D.ids_of_type(ds, a.syn_partner_type))
                    p = xyz[keep]
                    if e == "pre" and len(p):
                        p = np.unique(np.round(p, 2), axis=0)
                    syn[(nid, e, "all")] = len(syn[(nid, e)])
                    syn[(nid, e)] = p
    n_syn = sum(len(p) for k, p in syn.items() if len(k) == 2)
    frac = min(1.0, MAX_SYN / n_syn) if n_syn else 1.0
    rng = np.random.default_rng(0)

    def topn(d):
        s_in = sum(d.values())
        return [[names[r - 1], round(v / s_in, 3)] for r, v in sorted(d.items(), key=lambda x: -x[1])[:3]] if s_in else []

    for gi, (q, hits) in enumerate(groups):
        base = MAIN_WITH_PARTNERS if dirs and len(groups) == 1 else palette[gi % len(palette)]
        for k, (nid, typ, sd) in enumerate(hits):
            lab = f"{typ or '無型別'}{('（' + sd + '）') if sd else ''} {nid}"
            row = dict(id=nid, type=typ, side=sd)
            a_sw = D.read_skeleton(ds, nid)
            rl = D.region_lengths(ds, a_sw)
            for r, v in rl.items():
                tot_len[r] = tot_len.get(r, 0) + v
            row["top"] = topn(rl)
            if "fibre" in show:
                keep = max(1, int(np.ceil(len(a_sw) * n_total / MAX_PTS)))
                neu_items.append(lines_item(lab, D.FL.swc_polylines(a_sw, keep_every=keep), color=shade(base, k, len(hits))))
            for e in ends:
                p = syn[(nid, e)]
                rc = D.region_counts(ds, p)
                for r, v in rc.items():
                    tot_syn[r] = tot_syn.get(r, 0) + v
                row[e] = len(p)
                if a.syn_partner_type:
                    row[e + "_all"] = syn[(nid, e, "all")]
                row[e + "_top"] = topn(rc)
                if frac < 1 and len(p):
                    p = p[rng.random(len(p)) < frac]
                row[e + "_drawn"] = len(p)
                if len(p):
                    syn_items[e].append(points_item(f"{lab} {'輸出點' if e == 'pre' else '輸入點'}", p,
                                                    color=PRE_COLOR if e == "pre" else POST_COLOR, size=5.0, opacity=0.85))
            rows.append(row)
            print(f"  {lab}：骨架 {len(a_sw)} 點，纖維主要腦區 {row['top']}"
                  + "".join(f"；{e} {row[e]:,}（畫 {row[e + '_drawn']:,}）主要 {row[e + '_top']}" for e in ends))

    # 3. 腦區
    basis = "fibre" if ("fibre" in show or not tot_syn) else "syn"
    tot = tot_len if basis == "fibre" else tot_syn
    if a.regions == "none":
        regs = []
    elif a.regions == "auto":
        s = sum(tot.values()) or 1
        regs = [names[r - 1] for r, v in sorted(tot.items(), key=lambda x: -x[1]) if v / s >= 0.03][:12]
        if not regs and tot:
            regs = [names[max(tot, key=tot.get) - 1]]
    else:
        regs = [x.strip() for x in a.regions.split(",") if x.strip()]
        bad = [r for r in regs if r not in names]
        if bad:
            sys.exit(f"不認得的腦區：{bad}；可用的有：{', '.join(names)}")
    reg_items = []
    for i, r in enumerate(regs):
        v, f = D.region_mesh(ds, r, faces=1500)
        reg_items.append(mesh_item(r, v, f, color=REG_COLORS[i % len(REG_COLORS)], opacity=0.3))
    sc_groups = [{"name": "神經元（纖維）", "items": neu_items}] if neu_items else []
    for d in dirs:
        its = []
        sel = part[d]["sel"]
        for k, p in enumerate(sel):
            a_sw = D.read_skeleton(ds, p["id"])
            keep = max(1, int(np.ceil(len(a_sw) * n_total / MAX_PTS)))
            lab = f"{p['type'] or '無型別'}{('（' + p['side'] + '）') if p['side'] else ''} {p['id']}（{p['w']:,}）"
            its.append(lines_item(lab, D.FL.swc_polylines(a_sw, keep_every=keep),
                                  color=shade(UP_COLOR if d == "up" else DOWN_COLOR, k, len(sel)), width=1.0))
        if its:
            sc_groups.append({"name": "上游：送訊號給它（綠）" if d == "up" else "下游：接收它的訊號（橙）", "items": its})
    for e, nm in (("pre", "輸出點（pre，紅）"), ("post", "輸入點（post，藍）")):
        if syn_items[e]:
            sc_groups.append({"name": nm, "items": syn_items[e]})
    if reg_items:
        sc_groups.append({"name": "腦區", "items": reg_items})
    if not a.no_outline:
        ov, of = D.outline_mesh(ds)
        sc_groups.append({"name": "參考", "items": [mesh_item("整個神經系統輪廓", ov, of, color="#999999", opacity=0.05, ref=True)]})

    # 4. 存檔與清單
    tag = ("" if show == {"fibre"} else "-" + "-".join(x for x in ("fibre", "pre", "post") if x in show)) + "".join("-" + d for d in dirs) + ("-synf" if a.syn_partner_type else "")
    vid = a.id or re.sub(r"[^A-Za-z0-9_-]+", "-", f"{ds}-{a.neurons}-{a.side or ''}{tag}").strip("-")[:60]
    title = a.title or f"{a.neurons}" + (f"（{a.side}）" if a.side else "")
    os.makedirs(os.path.join(HERE, "views"), exist_ok=True)
    write_scene(os.path.join(HERE, "views", f"{vid}.json"), title, sc_groups, up=D.DS[ds]["up"], front=D.DS[ds]["front"])
    ix = [v for v in load_index() if v["id"] != vid]
    ix.insert(0, dict(id=vid, title=title, ds=ds, dataset=D.DS[ds]["label"], date=str(datetime.date.today()),
                      note=a.note, show=[x for x in ("fibre", "pre", "post") if x in show], sampled=round(frac, 3),
                      regions=regs, region_basis=basis,
                      region_frac=[round(tot.get(names.index(r) + 1, 0) / (sum(tot.values()) or 1), 3) for r in regs],
                      neurons=rows, partners=part or None, syn_filter=a.syn_partner_type or None))
    save_index(ix)
    print(f"畫面 {vid}：{n_total} 顆神經元、{len(regs)} 個腦區 {regs}")


if __name__ == "__main__":
    main()
