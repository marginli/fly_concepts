# -*- coding: utf-8 -*-
# 本條目影片的產生程式（原檔在 fly_multiwork/fly_firing_anim/make_anim.py；輸出 fly_firing_anim.mp4，複製到本資料夾改名 neuron_firing.mp4）。
"""fly_firing.docx 的動畫：從氣味到 KC 的完整訊號流程（約 2.5 分鐘，1920×1080，24 fps，畫面字幕，同步膜電位曲線）。
用法：python3 make_anim.py [--frames 0,100,...]（只輸出指定影格 PNG 預覽）；不帶參數＝全部影格平行輸出再用 ffmpeg 合成 mp4。"""
import os, sys, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse, Rectangle, Polygon, FancyArrowPatch
HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24
plt.rcParams.update({"font.family": ["Noto Sans CJK TC", "DejaVu Sans"], "font.size": 16, "axes.unicode_minus": False})
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"
NA, K, CL, YEL, MAG, VIO, RED, GRN, GRAY = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6", "#e34948", "#008300", "#9a9994"
OUTC, INC, LYM = "#f4f3ef", "#eaf1fb", "#fff3d6"

# ---------------- 場景與字幕 ----------------
SC = [  # (名稱, 秒數, [(開始比例, 字幕)])
 ("title", 6, [(0, "示意動畫，不按比例；動作放慢顯示，數值是大約值。")]),
 ("battery", 16, [(0, "每顆神經元都有自己的「電池」：細胞外鈉（Na⁺）多、鉀（K⁺）少，細胞內相反。"),
                  (0.35, "膜電位＝細胞內相對於細胞外的電壓。細胞內鉀多，靜止時鉀從漏電通道流出去，細胞內少了正電荷，所以膜電位是負的，約 −55 mV。"),
                  (0.7, "鈉鉀幫浦（Na⁺/K⁺-ATPase）用 ATP（細胞的能量分子）把鈉搬出去、鉀搬進來，維持這個濃度差。")]),
 ("receptor", 24, [(0, "氣味分子從感覺毛（sensillum）壁上的小孔進來，結合嗅覺受器神經元樹突上的氣味受體（OR＋Orco）。"),
                   (0.25, "這個受體本身就是一扇門。門一打開，帶正電的離子流進樹突，主要是鉀，膜電位升高。"),
                   (0.5, "這裡鉀往「裡面」流，和第 1 段相反，因為樹突泡在特殊的液體裡：感覺毛淋巴液的鉀和細胞內一樣多，濃度差不再把鉀往外推。"),
                   (0.75, "淋巴液的電壓又比一般體液高約 +35 mV；樹突內約 −55，比淋巴液低約 90 mV（右下的電壓尺），所以帶正電的鉀被吸進樹突。")]),
 ("spike", 20, [(0, "起始區（spike initiation zone）是產生動作電位的地方。輸入讓這裡的膜電位慢慢升高，接近門檻（threshold）。"),
                (0.2, "越過門檻，電壓門控鈉通道打開。鈉流進來，膜電位衝向 +50 mV 附近：這是動作電位（action potential）的上升。本片說的「放電」就是產生一次動作電位。"),
                (0.45, "鈉通道很快失活：門還開著，但孔道被塞子（黑點）塞住，鈉過不去。較慢的鉀通道打開，鉀流出去，膜電位回落。"),
                (0.75, "鉀門還沒全關，膜電位短暫低於靜止；鈉通道也還被塞住，這段時間很難再放電，叫不反應期（refractory period）。")]),
 ("axon", 13, [(0, "電荷擴散到旁邊一小段軸突，讓那一段也越過門檻，用自己的電池再產生一次動作電位。"),
               (0.5, "這樣一段接一段傳到嗅葉（腦中第一個處理氣味的地方），不會變弱；剛放過電的那段在不反應期，所以只往前傳。")]),
 ("synapse", 18, [(0, "動作電位到達軸突末梢，末梢的鈣通道打開，鈣（Ca²⁺）流進來。"),
                  (0.33, "鈣讓突觸小泡放出乙醯膽鹼（acetylcholine）。上下游之間隔著突觸間隙，上游的電流過不去，只有化學物質能過去。"),
                  (0.66, "乙醯膽鹼打開下游細胞的門（綠色方塊變黃），鈉進、鉀出；鈉的作用比較大，所以下游的膜電位升高。一個放出點同時對著好幾個下游細胞。")]),
 ("pn", 21, [(0, "下游是嗅葉的投射神經元（PN）。乙醯膽鹼打開的門讓鈉進、鉀出，用的是 PN 自己的電池。"),
             (0.3, "一次輸入只讓膜電位升一點，叫興奮性突觸後電位（EPSP），幾十毫秒內就消退；零星的輸入疊不起來。"),
             (0.6, "帶同一種氣味受體的許多嗅覺受器神經元都在放電，輸入一個接一個擠在短時間內，前一個還沒消退就疊上去（時間加總），PN 越過門檻放電。")]),
 ("kc", 22, [(0, "PN 把訊號送到蕈狀體（果蠅腦中負責氣味學習與記憶的構造），交給 Kenyon 細胞（KC）。每顆 KC 接收好幾顆 PN 的輸入。"),
             (0.25, "KC 比一般神經元難放電：要從靜止上升約 21.5 mV 才放電，一次輸入只有約 1.4 mV，21.5 ÷ 1.4 ≈ 15：要在短時間內收到 15 次以上。活躍的 PN 各放電好幾次，KC 甲收到夠多，越過門檻。"),
             (0.7, "只有同時收到夠多活躍 PN 的 KC 會放電。真實的腦裡，APL 神經元（蕈狀體裡一顆大的抑制性神經元）還會回頭讓 KC 更難越過門檻，所以一種氣味只讓少數 KC 放電。")]),
 ("energy", 13, [(0, "每一步的離子都是被濃度差或電壓推著自然流動（例如第 2 段的鉀是被電壓吸進去），當場不用花能量；一次放電流進來的鈉，只占細胞內原有鈉的百分之零點幾。"),
                 (0.5, "鈉鉀幫浦事後用 ATP 把離子搬回原位。輸入只負責「開門」，放電的能量來自每顆神經元自己的電池。")]),
 ("summary", 10, [(0, "整條路上，每顆神經元都用自己的電池重新產生訊號；神經元之間靠化學物質「開門」傳遞。")]),
]
T_START = np.cumsum([0] + [s[1] for s in SC]); TOTAL = T_START[-1]; NF = int(TOTAL * FPS)
def scene_at(t):
    i = min(int(np.searchsorted(T_START, t, side="right") - 1), len(SC) - 1)
    return i, (t - T_START[i]) / SC[i][1]
def subtitle(i, p):
    s = [x for x in SC[i][2] if x[0] <= p]; return s[-1][1] if s else ""

# ---------------- 小工具 ----------------
R = np.random.default_rng(7)
def ss(a, b, p):  # smoothstep
    x = np.clip((p - a) / (b - a), 0, 1); return x * x * (3 - 2 * x)
def dots(ax, xy, c, r=0.13, alpha=1.0, z=5):
    for x, y in xy: ax.add_patch(Circle((x, y), r, color=c, alpha=alpha, zorder=z, lw=0))
def legend_ions(ax, items, x=0.3, y=8.6):
    for k, (c, t) in enumerate(items):
        ax.add_patch(Circle((x + 0.15, y - k * 0.45), 0.13, color=c, zorder=6)); ax.text(x + 0.45, y - k * 0.45, t, va="center", fontsize=14, color=INK, zorder=6)
def arrow(ax, p, q, c=INK2, lw=2, ms=18, z=4):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw, zorder=z))
def membrane_h(ax, y, x0, x1, th=0.35, c=GRAY):
    ax.add_patch(Rectangle((x0, y - th / 2), x1 - x0, th, color=c, zorder=2))
def gate(ax, x, y, c, state, th=0.35, w=0.5):
    """state：0 關、1 開、2 失活（開但被塞住）"""
    if state == 0: ax.add_patch(Rectangle((x - w / 2, y - th / 2 - 0.08), w, th + 0.16, color=c, zorder=3))
    else:
        for dx in (-w / 2, w / 2 - 0.16): ax.add_patch(Rectangle((x + dx, y - th / 2 - 0.08), 0.16, th + 0.16, color=c, zorder=3))
        if state == 2: ax.add_patch(Circle((x, y - th / 2 - 0.05), 0.14, color=INK, zorder=4))
def flow(ax, x, y0, y1, n, phase, c, spread=0.12):
    """n 個離子沿 y0→y1 流動（phase 0–1 循環）"""
    for k in range(n):
        f = (phase + k / n) % 1; ax.add_patch(Circle((x + spread * np.sin(7 * k), y0 + (y1 - y0) * f), 0.12, color=c, zorder=5, alpha=0.95))

# ---------------- 膜電位曲線 ----------------
def hh_trace(n=1000, T=12.0):
    dt = T / n; V, m, h, nn = -65.0, 0.05, 0.6, 0.32; out = []
    for k in range(n):
        t = k * dt; I = 12 if 1 <= t < 2.2 else 0
        am = 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10)); bm = 4 * np.exp(-(V + 65) / 18)
        ah = 0.07 * np.exp(-(V + 65) / 20); bh = 1 / (1 + np.exp(-(V + 35) / 10))
        an = 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10)); bn = 0.125 * np.exp(-(V + 65) / 80)
        for _ in range(4):
            d = dt / 4; m += d * (am * (1 - m) - bm * m); h += d * (ah * (1 - h) - bh * h); nn += d * (an * (1 - nn) - bn * nn)
            V += d * (I - 120 * m ** 3 * h * (V - 50) - 36 * nn ** 4 * (V + 77) - 0.3 * (V + 54.4))
        out.append((V + 10, m ** 3 * h, nn ** 4))   # +10：靜止移到 −55，配合正文
    return np.array(out)
HH = hh_trace()
def epsp_train(times, T, w, tau=20.0, ts=5.0, n=1200, thr=None, v0=0.0, spike_to=None):
    dt = T / n; v = 0.0; g = 0.0; out = []; spikes = []; ti = sorted(times); j = 0; ref = 0
    for k in range(n):
        t = k * dt
        while j < len(ti) and ti[j] <= t: g += w; j += 1
        if ref > 0: ref -= dt; out.append(v); g -= dt / ts * g; continue
        v += dt / tau * (g - v); g -= dt / ts * g
        if thr is not None and v >= thr: spikes.append(t); out.append(spike_to); v = 0.0; g = 0.0; ref = 3.0; continue
        out.append(v)
    return np.arange(n) * dt, np.array(out), spikes
# 預先算好各場景曲線
TR = {}
t = np.linspace(0, 1, 1000)
TR["receptor"] = (np.linspace(0, 400, 1000), -55 + 10.5 * ss(0.33, 1.0, t), "傳到起始區的膜電位（mV）", -60, -30, [(-55, "靜止 −55"), (-45, "門檻（示意，下一段說明）")], "時間（毫秒）")
TR["spike"] = (np.linspace(0, 6, 1000), HH[:, 0], "起始區的膜電位（mV）", -80, 58, [(-55, "靜止"), (-45, "門檻（示意）"), (50, "鈉把膜電位拉向這裡（約 +50）")], "真實時間（毫秒）")
_ta = np.linspace(0, 6, 1000); _sh = 1.5
TR["axon"] = (_ta, HH[:, 0], "軸突上兩個位置的膜電位（mV）", -80, 58, [(-55, "靜止")], "真實時間（毫秒）")
TR["synapse"] = (np.linspace(0, 6, 1000), np.r_[HH[60:, 0], np.full(60, HH[-1, 0])], "上游末梢與下游細胞的膜電位（mV）", -80, 58, [(-55, "靜止")], "真實時間（毫秒）")
_pk0 = epsp_train([10.0], 100, 1.0)[1].max()
_pn_in = list(np.sort(R.uniform(0, 160, 6))) + list(np.sort(R.uniform(175, 265, 60)))
_tp, _vp, _spk = epsp_train(_pn_in, 300, 2.0 / _pk0, thr=10.0, spike_to=105.0)
TR["pn"] = (_tp, _vp - 55, "PN 的膜電位（mV；放電畫成一條直線）", -60, 55, [(-55, "靜止"), (-45, "門檻（示意）")], "真實時間（毫秒）"); PN_IN = _pn_in
_ka = list(np.sort(R.uniform(60, 72, 28))); _kb = list(np.sort(R.uniform(40, 200, 6)))
_pk = epsp_train([10.0], 100, 1.0)[1].max(); _wk = 1.4 / _pk
_tk, _vka, _s = epsp_train(_ka, 220, _wk, thr=21.5, spike_to=40.0)
_ka = [x for x in _ka if x <= _s[0]]; _tk, _vka, _ = epsp_train(_ka, 220, _wk, thr=21.5, spike_to=40.0)
_, _vkb, _ = epsp_train(_kb, 220, _wk)
TR["kc"] = (_tk, (_vka, _vkb), "KC 的膜電位：以靜止為 0，比靜止高多少（mV）", -3, 45, [(0, "靜止＝0"), (21.5, "門檻：比靜止高 21.5")], "真實時間（毫秒）"); KC_IN = (_ka, _kb)

WARP = {"spike": ([0, 0.2, 0.45, 0.75, 1], [0, 1.15, 1.5, 2.75, 6]), "kc": ([0, 0.25, 0.7, 1], [0, 58, 76, 220])}
def ms_of(name, p):
    tt = TR[name][0]
    if name in WARP: return float(np.interp(p, *WARP[name]))
    return tt[0] + p * (tt[-1] - tt[0])

def draw_trace(ax, name, p):
    ax.cla(); ax.set_facecolor("white")
    if name not in TR:
        ax.axis("off"); return
    tt, vv, lab, lo, hi, lines, xl = TR[name]
    n = len(tt); k = max(1, int(np.searchsorted(tt, ms_of(name, p), side='right')))
    for y, s in lines:
        ax.axhline(y, color=RED if "門檻" in s else GRAY, ls="--" if "門檻" in s else ":", lw=1.5)
        ax.text(tt[0] + 0.02 * (tt[-1] - tt[0]) if "門檻" in s else tt[-1], y, s, ha="left" if "門檻" in s else "right", va="bottom", fontsize=13, color=RED if "門檻" in s else INK2, zorder=5, bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))
    if name == "axon":
        ax.plot(tt[:k], vv[:k], color=RED, lw=2.5, label="位置 1（靠近起始區）")
        sh = int(_sh / 12 * n); v2 = np.r_[np.full(sh, vv[0]), vv[:n - sh]]
        ax.plot(tt[:k], v2[:k], color=VIO, lw=2.5, label="位置 2（較遠，晚一點）")
        ax.legend(loc="upper right", fontsize=12, frameon=False)
    elif name == "synapse":
        ax.plot(tt[:k], vv[:k], color=INK, lw=2.5, label="上游末梢")
        post = -55 + 6 * np.clip((tt - 3.3) / 1.0, 0, 1) * np.exp(-np.clip(tt - 4.3, 0, None) / 4)
        ax.plot(tt[:k], post[:k], color=GRN, lw=3, label="下游細胞（升高一點）"); ax.legend(loc="upper right", fontsize=13, frameon=False)
    elif name == "kc":
        ax.plot(tt[:k], vv[0][:k], color=RED, lw=2.5, label="KC 甲（收到很多輸入）"); ax.plot(tt[:k], vv[1][:k], color=GRAY, lw=2.5, label="KC 乙（輸入少）")
        ax.legend(loc="upper right", fontsize=13, frameon=False)
    else:
        ax.plot(tt[:k], vv[:k], color=INK, lw=2.5); ax.plot(tt[k - 1], vv[k - 1], "o", color=RED, ms=9)
    ax.set_xlim(tt[0], tt[-1]); ax.set_ylim(lo, hi); ax.set_title(lab, fontsize=15, color=INK)
    ax.set_xlabel(xl, fontsize=13); ax.tick_params(labelsize=12)
    for s in ("top", "right"): ax.spines[s].set_visible(False)

# ---------------- 各場景主畫面 ----------------
def sc_title(ax, p):
    ax.text(8, 5.4, "果蠅神經元怎麼傳遞訊號", ha="center", fontsize=46, color=INK, alpha=ss(0, 0.2, p))
    ax.text(8, 4.0, "從氣味到蕈狀體的 Kenyon 細胞", ha="center", fontsize=28, color=INK2, alpha=ss(0.1, 0.3, p))
    steps = ["氣味", "嗅覺受器", "起始區放電", "軸突", "突觸", "投射神經元", "Kenyon 細胞"]
    for k, s in enumerate(steps):
        x = 1.3 + k * 2.25; a = ss(0.3 + k * 0.07, 0.4 + k * 0.07, p)
        ax.add_patch(FancyBboxPatch((x - 0.95, 1.6), 1.9, 0.8, boxstyle="round,pad=0.05", color="#eef3fb", ec=NA, alpha=a, lw=1.5))
        ax.text(x, 2.0, s, ha="center", va="center", fontsize=14, alpha=a)
        if k < len(steps) - 1: ax.annotate("", xy=(x + 1.3, 2.0), xytext=(x + 0.97, 2.0), arrowprops=dict(arrowstyle="-|>", color=INK2, alpha=a))

def sc_battery(ax, p, energy=False):
    ax.add_patch(Rectangle((0, 4.8), 16, 4.2, color=OUTC)); ax.add_patch(Rectangle((0, 0), 16, 4.2, color=INC))
    membrane_h(ax, 4.5, 0, 16, th=0.6)
    ax.text(15.8, 8.7, "細胞外", ha="right", fontsize=18, color=INK2); ax.text(15.8, 0.3, "細胞內", ha="right", fontsize=18, color=INK2)
    rr = np.random.default_rng(3)
    out_na = rr.uniform([0.5, 5.2], [10.5, 8.6], (34, 2)); out_k = rr.uniform([0.5, 5.2], [10.5, 8.6], (5, 2))
    in_k = rr.uniform([0.5, 0.4], [10.5, 3.8], (34, 2)); in_na = rr.uniform([0.5, 0.4], [10.5, 3.8], (5, 2))
    jit = lambda a: a + 0.08 * np.sin(p * 40 + np.arange(len(a))[:, None] * 1.7)
    dots(ax, jit(out_na), NA); dots(ax, jit(in_na), NA); dots(ax, jit(out_k), K); dots(ax, jit(in_k), K)
    # 幫浦
    px = 13.0; ax.add_patch(FancyBboxPatch((px - 0.8, 3.9), 1.6, 1.2, boxstyle="round,pad=0.05", color="#e8e2f5", ec=VIO, lw=2, zorder=3))
    ax.text(px, 6.5, "鈉鉀幫浦", ha="center", fontsize=15, color=VIO, zorder=4)
    arrow(ax, (px - 1.2, 4.0), (px - 1.2, 5.6), c=NA, lw=2, ms=14); arrow(ax, (px + 1.2, 5.6), (px + 1.2, 4.0), c=K, lw=2, ms=14)
    sp = 3 if energy else 1.2; ph = (p * sp * 6) % 1
    for k in range(3): ax.add_patch(Circle((px - 0.45 + 0.45 * k, 3.6 + 2.2 * ph), 0.13, color=NA, zorder=5))
    for k in range(2): ax.add_patch(Circle((px - 0.25 + 0.5 * k, 5.6 - 2.2 * ph), 0.13, color=K, zorder=5))
    ax.text(px, 3.0, "鈉往外搬、鉀往內搬，用掉 ATP", ha="center", fontsize=13, color=VIO)
    # 漏電通道
    gate(ax, 10.0, 4.5, K, 1, th=0.6); flow(ax, 10.0, 3.8, 5.3, 2, (p * 3) % 1, K)
    ax.text(10.0, 5.7, "漏電通道\n（多半讓鉀過）", ha="center", fontsize=13, color=INK, zorder=7, bbox=dict(boxstyle="round", fc="white", ec=GRAY))
    legend_ions(ax, [(NA, "鈉 Na⁺"), (K, "鉀 K⁺")], x=0.3, y=4.0 - 0.0) if False else None
    ax.add_patch(Circle((0.5, 9.4), 0.0))
    for k, (c, s) in enumerate([(NA, "鈉 Na⁺"), (K, "鉀 K⁺")]):
        ax.add_patch(Circle((12.0 + k * 2.0, 8.4), 0.13, color=c, zorder=6)); ax.text(12.25 + k * 2.0, 8.4, s, va="center", fontsize=14)
    if energy:
        ax.text(5.5, 4.5, "放電時流動的離子很少；幫浦事後把它們搬回原位", ha="center", va="center", fontsize=15, color="white", zorder=6)
    else:
        ax.text(5.5, 4.5, "細胞膜（離子只能經過膜上的門或幫浦）", ha="center", va="center", fontsize=15, color="white", zorder=6)

def sc_receptor(ax, p):
    ax.add_patch(Rectangle((0, 0), 16, 2.2, color=OUTC)); ax.text(0.3, 1.6, "血淋巴（一般的體液）", fontsize=14, color=INK2)
    hair = Polygon([[3.2, 2.2], [9.8, 2.2], [7.6, 9.0], [5.4, 9.0]], color=LYM, ec=YEL, lw=3); ax.add_patch(hair)
    ax.text(9.6, 8.3, "感覺毛（sensillum）\n裡面是淋巴液：鉀很高", fontsize=15, color=INK)
    for yy in (5.5, 7.0, 8.2):   # 壁上小孔
        xl = 3.2 + (yy - 2.2) / 6.8 * 2.2; ax.add_patch(Rectangle((xl - 0.25, yy - 0.15), 0.5, 0.3, color="white", zorder=3))
    ax.text(1.0, 6.2, "壁上的小孔", fontsize=13, color=INK2)
    ax.add_patch(Rectangle((6.35, 1.0), 0.3, 7.4, color=GRN, zorder=3)); ax.text(6.9, 3.2, "樹突", fontsize=14, color=GRN)
    ax.add_patch(Ellipse((6.5, 1.0), 1.4, 0.9, color=YEL, zorder=3)); ax.text(7.4, 1.0, "細胞體", fontsize=13, va="center")
    ax.add_patch(Rectangle((6.35, 0.0), 0.3, 0.55, color=RED, zorder=3)); ax.text(7.0, 0.25, "起始區（下一段放大）", fontsize=13, color=RED, va="center")
    # 受體
    op = p > 0.32
    for yy in (5.0, 6.6):
        ax.add_patch(Rectangle((6.1, yy - 0.25), 0.25, 0.5, color=NA, zorder=4)); ax.add_patch(Rectangle((6.65, yy - 0.25), 0.25, 0.5, color=NA, zorder=4))
        if not op: ax.add_patch(Rectangle((6.35, yy - 0.25), 0.3, 0.5, color=NA, zorder=4))
    ax.text(9.9, 6.9, "氣味受體 OR＋Orco（門）", fontsize=15, color=NA); arrow(ax, (9.85, 7.0), (7.05, 6.65), c=NA, lw=1.5, ms=12)
    # 氣味分子
    for k in range(6):
        f = ss(0.02 + 0.04 * k, 0.3 + 0.03 * k, p); y0 = 8.2 if k % 2 else 7.0; x0 = 3.2 + (y0 - 2.2) / 6.8 * 2.2 - 1.5
        xx = x0 + (5.9 - x0) * f; yy = y0 + ((5.0 if k % 2 else 6.6) - y0) * f
        ax.add_patch(Polygon([[xx + 0.18 * np.cos(a), yy + 0.18 * np.sin(a)] for a in np.linspace(0, 2 * np.pi, 7)[:-1]], color=INK2, zorder=6))
    ax.text(1.2, 8.6, "氣味分子", fontsize=14, color=INK2)
    # 淋巴液中的鉀
    rr = np.random.default_rng(5); kk = rr.uniform([4.2, 2.6], [9.0, 8.4], (26, 2)); kk = kk[np.abs(kk[:, 0] - 6.5) > 0.6]
    dots(ax, kk + 0.06 * np.sin(p * 30 + np.arange(len(kk))[:, None]), K)
    if op:
        for yy in (5.0, 6.6):
            for k in range(3):
                f = ((p - 0.32) * 8 + k / 3) % 1; ax.add_patch(Circle((7.3 - 0.8 * f, yy + 0.1 * np.sin(k)), 0.13, color=K, zorder=5))
        ax.text(10.0, 5.6, "門打開 → K⁺ 流進樹突", fontsize=16, color=K)
    if p > 0.93: ax.text(9.8, 3.4, "起始區越過門檻 → 放電", fontsize=15, color=RED)
    ax.add_patch(Circle((10.3, 1.0), 0.13, color=K)); ax.text(10.55, 1.0, "鉀 K⁺", va="center", fontsize=14)
    if p > 0.5:
        bx = 13.2
        for yv, c, t_ in ((4.4, YEL, "淋巴液 +35"), (2.6, GRAY, "一般體液 0"), (0.4, INK, "樹突內 −55")):
            ax.plot([bx, bx + 0.8], [yv, yv], color=c, lw=4); ax.text(bx + 0.9, yv, t_, va="center", fontsize=13)
        ax.annotate("", xy=(bx + 0.4, 0.5), xytext=(bx + 0.4, 4.3), arrowprops=dict(arrowstyle="<->", color=RED, lw=2)); ax.text(bx + 0.55, 1.4, "相差約 90", ha="left", fontsize=13, color=RED)
        ax.text(bx - 0.6, 5.0, "電壓尺（mV）", fontsize=13, color=INK2)

def sc_spike(ax, p):
    ax.add_patch(Rectangle((0, 4.8), 16, 4.2, color=OUTC)); ax.add_patch(Rectangle((0, 0), 16, 4.2, color=INC))
    membrane_h(ax, 4.5, 0, 16, th=0.6)
    ax.text(0.3, 8.5, "起始區的細胞膜（放大）", fontsize=18, color=INK); ax.text(15.8, 8.6, "細胞外", ha="right", fontsize=16, color=INK2); ax.text(0.3, 0.3, "細胞內", ha="left", fontsize=16, color=INK2)
    # 對應 HH 時間
    tt = ms_of('spike', p) * 2; i = min(int(tt / 12 * len(HH)), len(HH) - 1); m3h, n4 = HH[i, 1], HH[i, 2]
    na_state = 0 if tt < 2.3 else (1 if tt < 3.0 else (2 if tt < 11.5 else 0))
    k_state = 1 if 3.0 <= tt < 11.5 else 0
    for x in (2.0, 5.0, 8.0): gate(ax, x, 4.5, NA, na_state, th=0.6)
    for x in (3.5, 6.5, 9.5): gate(ax, x, 4.5, K, k_state, th=0.6)
    if na_state == 1:
        for x in (2.0, 5.0, 8.0): flow(ax, x, 6.5, 3.0, 4, (p * 25) % 1, NA)
    if k_state == 1:
        for x in (3.5, 6.5, 9.5): flow(ax, x, 3.0, 6.5, 3, (p * 15) % 1, K)
    lab = {0: "鈉通道：關閉", 1: "鈉通道：打開，鈉流進來", 2: "鈉通道：失活（門開著但被塞住）"}[na_state]
    ax.text(11.2, 7.4, lab, fontsize=17, color=NA); ax.text(11.2, 6.6, "鉀通道：" + ("打開，鉀流出去" if k_state else "關閉"), fontsize=17, color=K)
    if 5.5 < tt: ax.text(11.2, 2.6, "不反應期", fontsize=20, color=INK2)
    ax.add_patch(Circle((11.4, 0.3), 0.14, color=INK)); ax.text(11.7, 0.3, "黑點＝塞住鈉通道的塞子（失活）", va="center", fontsize=13)
    for k, (c, s) in enumerate([(NA, "電壓門控鈉通道 / Na⁺"), (K, "電壓門控鉀通道 / K⁺")]):
        ax.add_patch(Rectangle((11.2, 1.6 - k * 0.6), 0.4, 0.3, color=c)); ax.text(11.8, 1.75 - k * 0.6, s, va="center", fontsize=13)

def sc_axon(ax, p):
    ax.add_patch(Rectangle((0, 0), 16, 9, color=OUTC))
    ax.add_patch(FancyBboxPatch((0.8, 3.6), 13.6, 1.8, boxstyle="round,pad=0.1", color=INC, ec=GRAY, lw=4))
    ax.text(0.8, 6.0, "起始區", fontsize=16, color=RED); ax.text(14.4, 6.6, "→ 軸突末梢，在嗅葉裡", fontsize=16, color=INK, ha="right")
    ms = ms_of('axon', p); pos = float(np.clip(3.0 + 6.0 * (ms - 1.5) / 1.5, 0.9, 14.0))
    if pos > 1.2: ax.add_patch(Rectangle((max(0.9, pos - 2.2), 3.62), min(2.2, pos - 0.9), 1.76, color=GRAY, alpha=0.6, zorder=3))
    ax.add_patch(Rectangle((pos - 0.25, 3.62), 0.9, 1.76, color=RED, alpha=0.85, zorder=4))
    for k in range(3): ax.add_patch(Circle((pos + 0.2, 6.0 - ((p * 30 + k / 3) % 1) * 1.6), 0.13, color=NA, zorder=5))
    arrow(ax, (pos + 0.9, 4.5), (pos + 1.9, 4.5), c=RED)
    ax.text(pos + 0.2, 2.9, "正在放電", ha="center", fontsize=15, color=RED); (ax.text(max(pos - 1.2, 1.5), 2.3, "不反應期", ha="center", fontsize=15, color=INK2) if pos > 2.2 else None)
    for x, s in ((3.0, "位置 1"), (9.0, "位置 2")): ax.plot([x, x], [5.4, 5.7], color=INK, lw=2); ax.text(x, 5.8, s, ha="center", fontsize=14, color=INK)
    for k, (c, s) in enumerate([(RED, "正在放電的一段"), (GRAY, "不反應期"), (NA, "鈉流進來")]):
        ax.add_patch(Rectangle((0.8 + k * 4.2, 0.6), 0.5, 0.35, color=c)); ax.text(1.45 + k * 4.2, 0.78, s, va="center", fontsize=14)

def sc_synapse(ax, p):
    ax.add_patch(Rectangle((0, 0), 16, 9, color=OUTC))
    ax.add_patch(Ellipse((8, 6.8), 8.0, 4.0, color=INC, ec=GRAY, lw=4, zorder=2)); ax.text(8, 8.95, "上游：嗅覺受器的軸突末梢", ha="center", fontsize=16)
    flash = ss(0.0, 0.05, p) * (1 - ss(0.12, 0.2, p))
    if flash > 0: ax.add_patch(Ellipse((8, 6.8), 8.0, 4.0, color=RED, alpha=0.25 * flash, zorder=3))
    ax.add_patch(Polygon([[7.2, 5.0], [8.8, 5.0], [8.8, 5.2], [8.1, 5.2], [8.1, 5.9], [7.9, 5.9], [7.9, 5.2], [7.2, 5.2]], color=INK, zorder=4))
    ax.text(9.0, 4.5, "T-bar（放出點）", fontsize=14)
    ax.text(12.4, 7.6, "突觸小泡\n（裝著乙醯膽鹼）", fontsize=13, color=MAG)
    ax.text(0.4, 4.1, "突觸間隙：上下游的膜之間，\n電流過不去，化學物質才過得去", fontsize=13, color=INK2)
    cop = p > 0.08
    for x, y in ((4.5, 6.2), (11.5, 6.2)):
        ax.add_patch(Rectangle((x - 0.2, y - 0.3), 0.4, 0.6, color=VIO, zorder=4))
        if cop and p < 0.45:
            for k in range(3):
                f = ((p - 0.08) * 10 + k / 3) % 1; dx = -1 if x < 8 else 1
                ax.add_patch(Circle((x + dx * (1.2 - 1.2 * f), y + 0.1 * k), 0.12, color=VIO, zorder=5))
    ax.text(3.6, 7.4, "鈣通道", fontsize=14, color=VIO, ha="center")
    # 小泡
    rr = np.random.default_rng(2); vs = rr.uniform([6.0, 6.3], [10.0, 8.0], (8, 2)); vs[0] = (8.0, 6.3)
    for k, (x, y) in enumerate(vs):
        if k == 0:
            f = ss(0.33, 0.48, p); yy = y - 0.9 * f
            if p < 0.5: ax.add_patch(Circle((x, yy), 0.32, color="white", ec=MAG, lw=2.5, zorder=5)); ax.add_patch(Circle((x, yy), 0.12, color=MAG, zorder=6))
        else: ax.add_patch(Circle((x, y), 0.32, color="white", ec=MAG, lw=2.5, zorder=5)); ax.add_patch(Circle((x, y), 0.12, color=MAG, zorder=6))
    posts = [(4.0, 2.0), (8.0, 1.6), (12.0, 2.0)]
    for x, y in posts:
        ax.add_patch(Ellipse((x, y), 2.8, 2.0, color="#f7f6f3", ec=GRAY, lw=3, zorder=2))
        opened = p > 0.72
        ax.add_patch(Rectangle((x - 0.35, y + 0.85), 0.7, 0.3, color=GRN if not opened else "#ffe14d", zorder=4))
    ax.text(14.4, 1.0, "三個不同的\n下游細胞", fontsize=14, ha="center")
    if p > 0.48:
        f = ss(0.48, 0.72, p)
        for k in range(15):
            tx, ty = posts[k % 3]; tx += 0.3 * np.sin(k); ty += 1.15
            ax.add_patch(Circle((8.0 + (tx - 8.0) * f, 4.9 + (ty - 4.9) * f), 0.1, color=MAG, zorder=6))
    if p > 0.75:
        for x, y in posts:
            flow(ax, x - 0.15, y + 1.6, y + 0.2, 2, (p * 10) % 1, NA); flow(ax, x + 0.25, y + 0.3, y + 1.6, 2, (p * 8) % 1, K)
            arrow(ax, (x - 0.55, y + 1.5), (x - 0.55, y + 0.3), c=NA, lw=1.5, ms=12); arrow(ax, (x + 0.65, y + 0.3), (x + 0.65, y + 1.5), c=K, lw=1.5, ms=12)
    leg = [(VIO, "鈣 Ca²⁺"), (MAG, "乙醯膽鹼")] + ([(NA, "鈉 Na⁺"), (K, "鉀 K⁺")] if p > 0.7 else [])
    ax.add_patch(Rectangle((10.6, 3.6), 0.6, 0.25, color=GRN)); ax.text(11.35, 3.72, "下游的受體（門）；變黃＝打開", va="center", fontsize=13)
    for k, (c, s) in enumerate(leg):
        ax.add_patch(Circle((0.5, 8.5 - k * 0.5), 0.13, color=c, zorder=6)); ax.text(0.8, 8.5 - k * 0.5, s, va="center", fontsize=13)

def sc_pn(ax, p):
    ax.add_patch(Rectangle((0, 0), 16, 9, color=OUTC))
    ax.add_patch(Ellipse((8.0, 4.5), 5.0, 4.6, color="#f3f0fb", ec=VIO, lw=2, ls="--")); ax.text(8.0, 7.1, "嗅小球：同一種嗅覺受器神經元的軸突匯集處", ha="center", fontsize=14, color=VIO)
    ax.add_patch(Rectangle((7.85, 3.0), 0.3, 3.2, color=GRN, zorder=3)); ax.plot([8.0, 8.0, 14.5], [3.0, 1.2, 1.2], color=NA, lw=6, zorder=3)
    ax.text(14.5, 1.6, "PN 軸突 → 蕈狀體", fontsize=15, ha="right", color=NA)
    ax.add_patch(Rectangle((8.4, 1.05), 0.6, 0.3, color=RED, zorder=4)); ax.text(9.1, 0.55, "PN 起始區", fontsize=13, color=RED)
    ax.text(8.4, 5.8, "PN 樹突", fontsize=13, color=GRN)
    tms = p * 300
    for k in range(6):
        y = 2.0 + k * 0.85; ax.plot([0.5, 7.6], [y, 4.5 + (y - 4.25) * 0.4], color=GRAY, lw=3, alpha=0.8, zorder=2)
        ax.add_patch(Circle((7.6, 4.5 + (y - 4.25) * 0.4), 0.18, color=GRAY, zorder=3))
    ax.text(0.3, 7.6, "許多同一種嗅覺受器神經元的軸突（灰線）", fontsize=14, color=INK2)
    recent = [ti for ti in PN_IN if tms - 8 < ti <= tms]
    for j, ti in enumerate(recent):
        k = int(ti * 7) % 6; y = 2.0 + k * 0.85; ty = 4.5 + (y - 4.25) * 0.4; f = (tms - ti) / 8
        ax.add_patch(Circle((7.6 + 0.3 * f, ty), 0.12, color=MAG, zorder=5))
        ax.add_patch(Circle((7.6 - 6.5 * (1 - f) * 0 + 0.0, ty), 0.0))
    spiking = any(abs(tms - s) < 4 for s in _spk)
    if spiking:
        ax.add_patch(Rectangle((8.4, 1.05), 0.6, 0.3, color=RED, zorder=4)); ax.text(11.0, 2.2, "PN 放電！", fontsize=22, color=RED)
    ax.text(10.8, 6.2, "粉紅點：乙醯膽鹼", fontsize=13, color=MAG); ax.text(10.8, 6.8, "灰色圓點：受器神經元的軸突末梢", fontsize=13, color=INK2)
    if tms < 165: ax.text(10.8, 4.6, "輸入零星：疊不起來", fontsize=17, color=INK2)
    else: ax.text(10.8, 4.6, "輸入密集：時間加總", fontsize=17, color=INK)

def sc_kc(ax, p):
    ax.add_patch(Rectangle((0, 0), 16, 9, color=OUTC))
    ax.add_patch(Ellipse((8.5, 4.6), 7.5, 7.0, color="#eef6ee", ec=GRN, lw=2, ls="--")); ax.text(8.5, 8.4, "蕈狀體的萼（calyx）", ha="center", fontsize=14, color=GRN)
    act = [True, True, True, True, False, False]
    ys = np.linspace(7.2, 1.8, 6)
    for k, (y, a) in enumerate(zip(ys, act)):
        ax.plot([0.4, 7.0], [y, y], color=NA if a else GRAY, lw=4 if a else 2, zorder=2)
        ax.text(0.4, y + 0.25, f"PN {k + 1}" + ("（活躍）" if a else "（安靜）"), fontsize=12, color=NA if a else INK2)
    KA, KB = (11.0, 6.0), (11.0, 3.0)
    for k, y in enumerate(ys):
        if act[k]: ax.plot([7.0, KA[0] - 0.6], [y, KA[1]], color=NA, lw=1.5, alpha=0.7)
    ax.plot([7.0, KB[0] - 0.6], [ys[0], KB[1]], color=NA, lw=1.5, alpha=0.7)
    for k, y in enumerate(ys[4:]): ax.plot([7.0, KB[0] - 0.6], [y, KB[1]], color=GRAY, lw=1.2)
    tms = ms_of("kc", p); ka_fire = any(abs(tms - s) < 2 for s in [t for t, v in zip(_tk, _vka) if v >= 39])
    ax.add_patch(Circle(KA, 0.6, color=RED if ka_fire else "#f7c9c9", zorder=4)); ax.text(KA[0] + 1.6, KA[1] + 0.6, "KC 甲" + ("  放電！" if ka_fire else ""), va="center", fontsize=16, color=RED)
    ax.add_patch(Circle(KB, 0.6, color="#dddcd8", zorder=4)); ax.text(KB[0] + 1.6, KB[1] + 0.6, "KC 乙：輸入不夠，\n不放電", va="center", fontsize=15, color=INK2)
    for ti in KC_IN[0]:
        if ti - 4 < tms <= ti + 0.3: f = min(1, 1 - (ti - tms) / 4); kk = int(ti * 10) % 4; ax.add_patch(Circle((7.0 + (KA[0] - 0.6 - 7.0) * f, ys[kk] + (KA[1] - ys[kk]) * f), 0.13, color=MAG, zorder=5))
    for ti in KC_IN[1]:
        if ti - 15 < tms <= ti: f = 1 - (ti - tms) / 15; ax.add_patch(Circle((7.0 + (KB[0] - 0.6 - 7.0) * f, ys[0] + (KB[1] - ys[0]) * f), 0.13, color=MAG, zorder=5))
    ax.text(0.4, 0.5, "粉紅點：PN 放電送來的輸入", fontsize=13, color=MAG)
    # APL
    if p > 0.66: ax.add_patch(FancyBboxPatch((12.2, 0.4), 3.3, 1.0, boxstyle="round,pad=0.05", color="#e9f6f0", ec=CL, lw=2)); ax.text(13.85, 0.9, "APL 神經元", ha="center", va="center", fontsize=14, color=CL)
    if p > 0.66:
        a = ss(0.66, 0.75, p); arrow(ax, (13.0, 1.5), (KA[0] + 0.3, KA[1] - 0.7), c=CL); arrow(ax, (12.8, 1.5), (KB[0] + 0.4, KB[1] - 0.6), c=CL)
        ax.text(12.1, 8.0, "真實的腦：KC 越活躍，APL 越強，\n回頭抑制 KC（右圖的計算沒有包含）", fontsize=12, color=CL, alpha=a)

def sc_summary(ax, p):
    steps = [("氣味分子", "打開受器樹突的門"), ("嗅覺受器", "鉀流進樹突"), ("起始區", "鈉進、鉀出：放電"), ("軸突", "一段接一段傳"),
             ("突觸", "鈣進，放出乙醯膽鹼"), ("投射神經元", "時間加總後放電"), ("Kenyon 細胞", "收到夠多才放電")]
    for k, (a, b) in enumerate(steps):
        x = 1.2 + k * 2.27; al = ss(k * 0.08, k * 0.08 + 0.1, p)
        ax.add_patch(FancyBboxPatch((x - 1.0, 4.2), 2.0, 1.6, boxstyle="round,pad=0.05", color="#eef3fb", ec=NA, lw=2, alpha=al))
        ax.text(x, 5.3, a, ha="center", fontsize=15, alpha=al); ax.text(x, 4.6, b, ha="center", fontsize=11, color=INK2, alpha=al)
        if k < len(steps) - 1: ax.annotate("", xy=(x + 1.27, 5.0), xytext=(x + 1.02, 5.0), arrowprops=dict(arrowstyle="-|>", color=INK2, alpha=al))
    ax.text(8, 2.4, "能量：每顆神經元的鈉鉀幫浦事後用 ATP 補電", ha="center", fontsize=17, color=VIO, alpha=ss(0.6, 0.75, p))

DRAW = {"title": sc_title, "battery": sc_battery, "receptor": sc_receptor, "spike": sc_spike, "axon": sc_axon, "synapse": sc_synapse,
        "pn": sc_pn, "kc": sc_kc, "energy": lambda ax, p: sc_battery(ax, p, energy=True), "summary": sc_summary}
TRACE_P = {"receptor": lambda p: p, "spike": lambda p: p, "axon": lambda p: p, "synapse": lambda p: p, "pn": lambda p: p, "kc": lambda p: p}
TITLES = {"battery": "1　電池：離子濃度差", "receptor": "2　氣味打開嗅覺受器神經元的門", "spike": "3　起始區產生動作電位", "axon": "4　沿軸突傳出去",
          "synapse": "5　化學突觸", "pn": "6　投射神經元：時間加總", "kc": "7　Kenyon 細胞：收到夠多才放電", "energy": "8　能量的帳", "summary": "整理"}

def wrap(st, n=50):
    lines = []
    while len(st) > n:
        cut = max([k + 1 for k, c in enumerate(st[:n]) if c in "，。；：、）"] or [n]); lines.append(st[:cut]); st = st[cut:]
    return "\n".join(lines + [st])

def render(fi, path):
    t = fi / FPS; i, p = scene_at(t); name = SC[i][0]
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100); fig.patch.set_facecolor("white")
    full = name in ("title", "battery", "energy", "summary")
    axm = fig.add_axes([0.12, 0.165, 0.76, 0.76] if full else [0.02, 0.2, 0.62, 0.62]); axm.set_xlim(0, 16); axm.set_ylim(0, 9); axm.axis("off")
    DRAW[name](axm, p)
    if not full:
        axt = fig.add_axes([0.69, 0.25, 0.29, 0.6]); draw_trace(axt, name, TRACE_P[name](p))
        if name in ("spike", "axon", "synapse", "pn", "kc"): axt.text(0.5, 1.09, "動畫放慢顯示；橫軸是真實時間", transform=axt.transAxes, ha="center", fontsize=13, color=INK2)
    if name in TITLES: fig.text(0.02, 0.955, TITLES[name], fontsize=26, color=INK, weight="bold")
    fig.add_artist(Rectangle((0, 0), 1, 0.155, transform=fig.transFigure, color="#1f1f1d", zorder=0))
    st = wrap(subtitle(i, p))
    fig.text(0.5, 0.0775, st, ha="center", va="center", fontsize=23, color="white", linespacing=1.45)
    fig.savefig(path, facecolor="white"); plt.close(fig)

def job(fi):
    render(fi, os.path.join(HERE, "frames", f"f{fi:05d}.png"))

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--frames":
        for fi in map(int, sys.argv[2].split(",")): render(fi, os.path.join(HERE, f"preview_{fi:05d}.png"))
        sys.exit()
    from multiprocessing import Pool
    FD = os.path.join(HERE, "frames"); os.makedirs(FD, exist_ok=True)
    with Pool(10) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, range(NF), chunksize=8)):
            if k % 360 == 0: print(f"第 {k // 360 + 1}/{NF // 360 + 1} 批 影格 {k}/{NF}", flush=True)
    os.system(f"ffmpeg -y -loglevel error -framerate {FPS} -i {FD}/f%05d.png -c:v libopenh264 -b:v 6M -pix_fmt yuv420p {HERE}/../fly_firing_anim.mp4")
    print("done")
