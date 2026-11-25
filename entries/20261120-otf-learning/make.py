# -*- coding: utf-8 -*-
# 本條目 demo.html 的產生程式（2026-11-25 改成「懲罰／獎賞」切換版）。
# 原始檔在 otf_port 移植包（實驗室工作站上）：fly_multiwork/onthefly/anim/
#   懲罰版：
#   1. run_sq.py（ARENA=corner SHOCK_MODE=rand TURN=S SINGLE=1，野生型 20＋關掉學習 20）→ out/sq1_main_S_corner8c5_rand.npz/.json
#   2. export_anim.py sq1_main_S_corner8c5_rand 18 23 anim_data.json
#      取兩組各自最接近組平均的那一隻（第 19、24 隻），輸出每 0.05 秒的位置、電擊、S 等，
#      以及連接強度在每段結束時的記錄值（w_end；段內沒有記錄，不推估）
#   獎賞版：
#   3. run_sq.py 同上，另加 OCT_TEST=1、US_TYPES=PAM02,PAM05,PAM06,PAM07,PAM08,PAM12,PAM13,PAM14
#      → out/sq1_main_S_corner8c5_rand_oct_us8.npz/.json
#   4. export_anim_reward.py sq1_main_S_corner8c5_rand_oct_us8 16 34 anim_data_reward.json
#      （第 17、35 隻；連接強度改用 KC→MBON09）
#   合併：
#   5. build_site_both.py <舊版單檔網頁> anim_data_reward.json site_both.html
#      兩份資料都包在同一個檔案裡，上方切換；同一份網頁也放在 https://marginli.github.io/fly-otf-animation/
#   6. 本程式：在 site_both.html 加上「告訴條目頁自己多高」的 script，iframe 會自動調整高度。
# 用法：python3 make.py <anim 資料夾>   （預設為上述移植包在本機的位置）
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANIM = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/work/from_desktopTC/otf_port_20261119/extracted/otf_port/fly_multiwork/onthefly/anim")

src = open(os.path.join(ANIM, "site_both.html"), encoding="utf-8").read()
assert 'id="anim-data-reward"' in src and src.count("</body>") == 1, "site_both.html 的格式變了，要更新本程式"
height = """<script>
// 在條目頁的 iframe 裡時，告訴外層內容的高度，iframe 會自動調整。
// 量 .wrap 的底（加上 body 的上下邊距），不可用 documentElement.scrollHeight：它至少等於 iframe 高度，
// 外層又會再加 4 px，兩邊互相觸發 resize，框就會一直變長。高度沒變就不送。
// 切換懲罰／獎賞時內容高度會變，用 ResizeObserver 跟著送。
let lastH = 0;
function sendH(){
  if (parent === window) return;
  const w = document.querySelector(".wrap"), cs = getComputedStyle(document.body);
  const h = Math.ceil(w.getBoundingClientRect().bottom + scrollY + parseFloat(cs.paddingBottom) + parseFloat(cs.marginBottom));
  if (Math.abs(h - lastH) > 1) { lastH = h; parent.postMessage({demoH: h}, "*"); }
}
addEventListener("load", sendH); addEventListener("resize", sendH); setTimeout(sendH, 500);
if (window.ResizeObserver) new ResizeObserver(sendH).observe(document.querySelector(".wrap"));
</script>
"""
out = src.replace("</body>", height + "</body>")
open(os.path.join(HERE, "demo.html"), "w", encoding="utf-8").write(out)
print("demo.html", len(out.encode()), "bytes")
