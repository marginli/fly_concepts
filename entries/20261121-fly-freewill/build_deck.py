#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""果蠅自由意志文獻回顧簡報。內容取自 ../fly_freewill.md（已冷讀 4 輪的報告），不另補事實。
版型沿用 ~/weekly_literature_review/tools/deck_lib.py。
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.expanduser('~/weekly_literature_review/tools'))
from deck_lib import *  # noqa

OUT = os.path.join(HERE, '..', 'fly_freewill.pptx')
SERIES = '果蠅的自由意志'
TOTAL = 16

prs = new_deck()


def cards_row(s, y, h, items, x0=MARGIN, gap=0.25, head_size=18, body_size=14, fill=TINT):
    """items：[(標號, 標題, 內文, 標號底色)]，平均分配寬度。"""
    n = len(items)
    w = (W - 2 * x0 - gap * (n - 1)) / n
    for i, (lab, head, body, col) in enumerate(items):
        x = x0 + i * (w + gap)
        box(s, x, y, w, h, fill=fill)
        if lab:
            circle_num(s, x + 0.2, y + 0.2, 0.6, lab, fill=col, size=14)
            text(s, x + 0.95, y + 0.25, w - 1.1, 0.5, head, size=head_size, bold=True, color=DARK)
        else:
            text(s, x + 0.2, y + 0.2, w - 0.4, 0.5, head, size=head_size, bold=True, color=DARK)
        text(s, x + 0.2, y + 0.95, w - 0.4, h - 1.05, body, size=body_size, color=TEXT)


def bignum(s, x, y, w, num, label, col=DARK):
    text(s, x, y, w, 0.9, num, size=40, bold=True, color=col, align=PP_ALIGN.CENTER)
    text(s, x, y + 0.9, w, 0.6, label, size=14, color=MUTED, align=PP_ALIGN.CENTER)


# ---------- 1. 標題 ----------
s = dark_slide(prs)
text(s, MARGIN + 0.1, 0.9, 11, 0.4, '文獻回顧 · 行為實驗、神經機制與電腦模擬', size=14, color=ACCENT, bold=True)
text(s, MARGIN + 0.1, 1.6, 11.5, 1.2, '果蠅有沒有自由意志？', size=48, color=WHITE, bold=True)
text(s, MARGIN + 0.1, 2.85, 11.5, 1.3,
     '外界不變時，果蠅的行為仍然會自己改變，而且改變有規律',
     size=26, color=LIGHT_ON_DARK)
for i, (lab, col, fc) in enumerate([('行為', ACCENT, DARK), ('神經', WHITE, DARK), ('模擬', TINT2, DARK)]):
    circle_num(s, MARGIN + 0.1 + i * 1.25, 4.55, 0.95, lab, fill=col, color=fc, size=14)
text(s, MARGIN + 0.1, 6.15, 11.5, 0.4,
     '2026-11-21　|　31 篇文獻，詳見報告 fly_freewill.docx',
     size=13, color=LIGHT_ON_DARK)
notes(s, '今天整理「果蠅有沒有自由意志」這個問題的文獻。'
         '先講結論：研究者沒辦法問果蠅「你是不是自己決定的」，所以把問題改成「外界不變時，行為會不會自己改變、改變有沒有規律」。'
         '答案是會，而且有規律。但這些實驗沒有證明果蠅有意識。'
         '內容分三塊：行為實驗、神經機制、電腦模擬。電腦模擬那一塊，目前還沒有人用全腦連結體做到「自己產生行為」，這可能是我們可以切入的地方。'
         '\n\n【備查，不用唸】\n學界英文是 free will，中文一般譯「自由意志」，有時也被寫成「自由意識」。'
         '完整的文獻與 DOI 在報告 fly_freewill.docx，報告經過 4 輪冷讀。')

# ---------- 2. 問題怎麼問 ----------
s = content_slide(prs, '把哲學問題換成三個可以量的問題', kicker='問題怎麼問',
                  page=2, total=TOTAL, series=SERIES)
qs = [('1', '外界不變時，行為會不會改變？'), ('2', '行為的改變有沒有結構（可以量出的規律）？'),
      ('3', '哪些神經元產生這些改變？')]
for i, (n, q) in enumerate(qs):
    y = 1.75 + i * 0.85
    circle_num(s, MARGIN, y, 0.6, n, fill=DARK, size=16)
    text(s, MARGIN + 0.8, y + 0.08, 5.6, 0.6, q, size=18, color=TEXT)
text(s, MARGIN, 4.45, 5.9, 2.2,
     [{'runs': [('不問：', {'bold': True, 'color': RED}), ('「果蠅覺得自己自由嗎？」（意識）', {})], 'bullet': True},
      {'runs': [('不問：', {'bold': True, 'color': RED}), ('決定論（一切都由先前原因完全決定）是否成立', {})], 'bullet': True}],
     size=15)
# 右邊：Brembs 兩階段
x0 = 7.1
box(s, x0, 1.6, 5.6, 5.0, fill=TINT)
text(s, x0 + 0.25, 1.75, 5.1, 0.5, 'Brembs（2011）的生物學定義', size=18, bold=True, color=DARK)
text(s, x0 + 0.25, 2.12, 5.1, 0.35, 'Björn Brembs：本次多數果蠅行為實驗的作者之一', size=11, color=MUTED)
box(s, x0 + 0.3, 2.45, 5.0, 1.25, fill=WHITE)
text(s, x0 + 0.45, 2.52, 4.7, 1.15,
     [[('第一階段　產生選項', {'bold': True, 'color': ACCENT})],
      '腦內微小的隨機波動被放大，外界無法事先準確預測'], size=14)
arrow(s, x0 + 2.5, 3.78, 0.6, 0.35, fill=MUTED)
s.shapes[-1].rotation = 90
box(s, x0 + 0.3, 4.2, 5.0, 1.25, fill=WHITE)
text(s, x0 + 0.45, 4.27, 4.7, 1.15,
     [[('第二階段　選一個', {'bold': True, 'color': DARK})],
      '依照動機、經驗和個性，從選項中選一個'], size=14)
text(s, x0 + 0.25, 5.6, 5.1, 0.95, '不需要意識；自由意志有程度之分。\n例：細菌先隨機轉向，再保留朝向食物的方向（Heisenberg 2009）',
     size=13, color=MUTED)
notes(s, '傳統的自由意志問題包括兩件事：有沒有意識，以及決定論是不是成立。這兩件事都沒辦法拿果蠅來回答。'
         '所以研究者改問左邊這三個可以量的問題。'
         '右邊是 Björn Brembs 2011 提出的定義。Brembs 是後面好幾個果蠅飛行模擬器實驗的作者之一。這也是本次回顧採用的定義：'
         '動物能自己產生不同的行為選項，再從中選一個。'
         '第一階段有不能預測的成分；第二階段依照動機和經驗選擇。這個定義不需要意識，而且有程度之分，問題變成「果蠅有多少」而不是「有沒有」。'
         'Heisenberg 2009 在 Nature 的短文用細菌當例子：先隨機改變方向，再保留朝向食物的方向，他認為這是最基本的形式。'
         '\n\n【備查，不用唸】\n這位 Heisenberg 是果蠅神經生物學家 Martin Heisenberg，不是物理學家 Werner Heisenberg。'
         'Brembs 也說明行為變異的好處：行為太好預測的動物容易被掠食者抓到。')

# ---------- 3. 工具 ----------
s = content_slide(prs, '兩種工具：沒有回饋的飛行，和邊走邊看腦', kicker='實驗工具',
                  page=3, total=TOTAL, series=SERIES)
cards_row(s, 1.7, 3.3, [
    ('1', '飛行模擬器', '果蠅黏在細桿上原地拍翅，儀器量想往左或往右轉的力量（扭力，yaw torque）。\n\n'
                    '開迴路（open loop）：轉向時畫面不跟著變，沒有回饋，四周也沒有新刺激 → 轉向主要由腦自己產生。\n'
                    '閉迴路（closed loop）：電腦依扭力轉動畫面，果蠅能控制看到的東西。', DARK),
    ('2', '球上走路＋腦影像', '頭或背固定，果蠅在浮在氣流上的球上走，攝影機記錄球的轉動。\n\n'
                         '同時用顯微鏡看腦：神經元帶螢光蛋白，活動時變亮（鈣離子影像）。', ACCENT),
], body_size=15)
text(s, MARGIN, 5.3, W - 2 * MARGIN, 1.2,
     [[('「一次轉向」怎麼算：', {'bold': True, 'color': ACCENT}),
       ('扭力突然出現一次短暫的大幅變化，就算一次快速轉向；再計算兩次轉向之間的時間間隔', {})]], size=15)
notes(s, '這個領域主要用兩種工具。第一種是飛行模擬器：果蠅黏在細桿上原地拍翅，儀器量扭力。'
         '開迴路時，果蠅轉向，畫面不會跟著變，所以沒有回饋、也沒有新刺激能引發轉向，這時候的轉向就是腦自己產生的。'
         '閉迴路時，電腦依照扭力轉動畫面，果蠅可以用自己的動作控制看到的東西，學習實驗都是用閉迴路。'
         '第二種是球上走路，大家應該比較熟：果蠅固定，在球上走，同時用顯微鏡做鈣離子影像。'
         '後面講到的「轉向間隔」，就是從扭力訊號切出一次一次的快速轉向，再算間隔。')

# ---------- 4. Maye 2007 ----------
s = content_slide(prs, '外界不變時，果蠅的轉向仍有長程規律', kicker='行為 1 · Maye 等人 2007',
                  page=4, total=TOTAL, series=SERIES)
for i, (n, l) in enumerate([('39', '隻雌果蠅'), ('30', '分鐘／隻'), ('3', '種條件，各 13 隻')]):
    bignum(s, MARGIN + i * 2.1, 1.6, 2.0, n, l)
text(s, MARGIN, 3.25, 6.2, 1.2,
     '條件：(1) 開迴路，四周全白（最接近無刺激）；(2) 閉迴路，一條黑色直條；(3) 閉迴路，均勻花紋。再和電腦產生的「隨機雜訊模型」比較。',
     size=14, color=TEXT)
box(s, MARGIN, 4.55, 6.2, 1.9, fill=TINT2)
text(s, MARGIN + 0.2, 4.65, 5.8, 1.75,
     [[('隨機雜訊模型：', {'bold': True}), ('每次轉向彼此獨立、機率固定', {})],
      '→ 連續很多次都不轉的機率是相乘，很快變小',
      '→ 預測：很長的間隔非常少見'], size=14)
res = [('冪律分布', '很長的間隔比隨機模型多得多。與 Lévy 飛行（動物覓食時多數走短、偶爾走很遠）同屬冪律'),
       ('長程相關', '不只上一次，前面好幾次的間隔長短，仍和現在的間隔有關'),
       ('非線性較準', '用過去的轉向資料預測下一段：允許彎曲關係的非線性方法比直線方法準 → 不是「雜訊加直線規則」')]
for i, (h, b) in enumerate(res):
    y = 1.6 + i * 1.62
    box(s, 7.15, y, 5.55, 1.45, fill=TINT)
    circle_num(s, 7.3, y + 0.42, 0.6, str(i + 1), fill=ACCENT, color=DARK, size=14)
    text(s, 8.1, y + 0.1, 4.5, 0.45, h, size=17, bold=True, color=DARK)
    text(s, 8.1, y + 0.53, 4.5, 0.9, b, size=13, color=TEXT)
text(s, 7.15, 6.5, 5.6, 0.45, '三種條件結果方向相同：都偏離隨機', size=13, color=MUTED)
notes(s, '第一個、也是最常被引用的實驗：Maye、Brembs 等人 2007 年 PLoS ONE。'
         '39 隻雌果蠅，每隻在飛行模擬器記錄 30 分鐘，分三種條件，第一種是開迴路全白，最接近沒有刺激。'
         '比較對象是隨機雜訊模型：每次轉向彼此獨立、機率固定。這種模型預測很長的間隔非常少見，因為連續很多次都不轉的機率是相乘的。'
         '結果有三點。第一，很長的間隔比隨機模型多很多。隨機模型的間隔分布是越長越快變少；冪律分布也是越長越少，但減少得慢，所以很長的間隔仍常出現。這跟動物覓食的 Lévy 飛行同一類。'
         '第二，間隔之間有長程相關。第三，用過去資料預測下一段：拿過去的轉向資料去預測接下來的轉向。如果轉向只是隨機雜訊，加上「下一次＝前幾次的固定比例相加」這種直線規則，直線（線性）的預測方法就夠了；結果是允許彎曲關係的非線性方法比較準，所以也排除了這種解釋。'
         '三種條件裡有兩種是閉迴路，用來比較有回饋時是否一樣；三種的結果方向相同。'
         '作者的結論：產生轉向的腦迴路是非線性、一直在變動的系統，行為是它自己產生的。'
         '注意「不是隨機雜訊」指的是行為本身；後面模擬會說腦內需要隨機波動，這不矛盾：腦內的微小起伏，被非線性迴路放大、塑造成有規律的行為。'
         '\n\n【備查，不用唸】\n限制：只看行為、沒看腦；只有 39 隻。'
         '作者認為許多動物都有 Lévy 類分布，可能代表共通的神經機制。'
         '「隨機雜訊」和後面模擬說的「腦內隨機波動」不矛盾：前者指行為本身每次獨立；後者是腦內微小起伏，經非線性迴路放大、塑造成有規律的行為。')

# ---------- 5. Martin 走路 ----------
s = content_slide(prs, '走與停的時間是碎形，阻斷橢圓體就消失', kicker='行為 2 · Martin 等人 1999、2001',
                  page=5, total=TOTAL, series=SERIES)
text(s, MARGIN, 1.6, W - 2 * MARGIN, 0.9,
     '單隻果蠅放在小管子裡，記錄數小時的走與停。碎形（fractal）：把時間尺度放大或縮小，「一陣一陣」的樣子看起來都相似。',
     size=15, color=TEXT)
steps = [('黑暗、沒有食物', '碎形模式出現\n程度隨性別、品系、年齡改變', DARK, WHITE),
         ('加入食物或光', '碎形模式消失\n行為較多由刺激決定', RED, WHITE),
         ('阻斷橢圓體輸出', '碎形模式也消失\n（Martin、Faure、Ernst 2001）', ACCENT, DARK)]
for i, (h, b, col, fc) in enumerate(steps):
    x = MARGIN + i * 4.1
    box(s, x, 2.75, 3.75, 2.6, fill=TINT)
    box(s, x, 2.75, 3.75, 0.7, fill=col)
    text(s, x + 0.15, 2.82, 3.45, 0.55, h, size=17, bold=True, color=fc, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, 3.65, 3.35, 1.6, b, size=15, color=TEXT, align=PP_ALIGN.CENTER)
text(s, MARGIN, 5.7, W - 2 * MARGIN, 0.8,
     [[('意義：', {'bold': True, 'color': ACCENT}),
       ('最早把「自發行為的時間規律」連到特定腦區（橢圓體，ellipsoid body）的實驗之一', {})]], size=16)
notes(s, '第二個是 Martin、Heisenberg 實驗室 1999 年的走路實驗。單隻果蠅放在小管子裡記錄好幾個小時。'
         '在黑暗、沒有食物時，走和停的時間是碎形模式，碎形的程度隨性別、品系、年齡改變，表示這個規律也受果蠅本身的因素影響。'
         '加入食物或光以後，碎形模式消失：有外界刺激時，行為比較多由刺激決定。'
         '2001 年同一組人阻斷橢圓體神經元的輸出，碎形模式也消失。這是最早把自發行為的時間規律連到特定腦區的實驗之一。'
         '\n\n【備查，不用唸】\n碎形程度用碎形維度衡量；數值大小的方向，報告沒有查到細節。')

# ---------- 6. Gorostiza 趨光 ----------
s = content_slide(prs, '同樣的光，不能飛的果蠅就不再走向光', kicker='行為 3 · Gorostiza 等人 2016',
                  page=6, total=TOTAL, series=SERIES)
flow = [('能飛', '偏好光亮處', DARK, WHITE),
        ('暫時不能飛', '剪短翅膀，或用濃糖水黏住翅膀\n→ 對光偏好降低或反轉為偏暗', RED, WHITE),
        ('洗掉糖水', '翅膀恢復\n→ 又偏好光亮處', ACCENT, DARK)]
for i, (h, b, col, fc) in enumerate(flow):
    x = MARGIN + i * 4.15
    box(s, x, 1.75, 3.6, 2.5, fill=TINT)
    circle_num(s, x + 1.35, 1.9, 0.9, str(i + 1), fill=col, color=fc, size=18)
    text(s, x + 0.15, 2.9, 3.3, 0.5, h, size=18, bold=True, color=DARK, align=PP_ALIGN.CENTER)
    text(s, x + 0.15, 3.4, 3.3, 0.85, b, size=14, color=TEXT, align=PP_ALIGN.CENTER)
    if i < 2:
        arrow(s, x + 3.67, 2.8, 0.42, 0.4)
text(s, MARGIN, 4.6, W - 2 * MARGIN, 1.9,
     [{'runs': [('光沒有改變，改變的是果蠅自己的狀態。', {'bold': True})], 'bullet': True},
      {'runs': '作者結論：果蠅會監測自己能不能飛；能不能飛，影響果蠅選哪一個動作', 'bullet': True},
      {'runs': '多巴胺神經元與章魚胺（octopamine）神經元的活動都與光偏好有關（兩者作用不同，細節見報告）', 'bullet': True},
      {'runs': '看起來固定的趨光性，也包含「權衡外界情況與自身狀態」的決定步驟', 'bullet': True}],
     size=16)
notes(s, '第三個是 Brembs 實驗室 2016 年的 Open Biology。果蠅走路時一般偏好光亮處，這常被當成固定反射。'
         '研究者暫時讓果蠅不能飛：剪短翅膀，或用濃糖水把兩片翅膀黏在一起。不能飛的果蠅，對光的偏好降低，甚至反轉成偏好暗處。'
         '用水洗掉糖水、翅膀恢復以後，又回到偏好光。'
         '光完全沒變，變的是果蠅自己的狀態，所以作者說果蠅會監測自己能不能飛，連趨光性這種看似固定的行為，都包含一個決定步驟。'
         '多巴胺和章魚胺神經元的活動都與這個偏好有關，但作用不同。')

# ---------- 7. 個體差異 ----------
s = content_slide(prs, '基因幾乎相同的果蠅，各有自己的習慣', kicker='行為 4 · 個體差異',
                  page=7, total=TOTAL, series=SERIES)
cards_row(s, 1.65, 3.85, [
    ('1', '左右轉偏好', 'Buchanan 等人 2015\n\nY 字迷宮中，每隻有自己的左右偏好；每個品系都有強烈偏向的個體。\n\n不遺傳。強度由中央複合體的柱狀神經元（columnar neurons）控制', DARK),
    ('2', '趨光個性', 'Kain 等人 2012\n\n每隻對光的偏好不同，維持一生、不遺傳。\n\n血清素與 white 基因壓低這種差異：它們作用減少時，個體差異變大', DARK),
    ('3', '接線決定個性', 'Linneweber 等人 2020\n\n視覺系統的背側叢神經元（DCN）左右接線不對稱程度因個體而異；越不對稱，朝看到的物體走得越直。\n\n讓 DCN 不活動，關係消失；人為增加不對稱，朝物體走得更好', DARK),
], body_size=14)
text(s, MARGIN, 5.75, W - 2 * MARGIN, 0.9,
     [[('意義：', {'bold': True, 'color': ACCENT}),
       ('差異來自發育中的隨機接線變化，不來自基因 → 行為不能完全由基因與環境預測', {})]], size=16)
notes(s, '這一張是個體差異。它們不直接研究自由意志，但說明一件事：同一品系、基因幾乎相同的果蠅，行為還是不一樣，而且這些差異不會遺傳。'
         '第一個，Buchanan 等人 2015，de Bivort 實驗室：Y 字迷宮中每隻果蠅有自己的左右偏好，每隻偏得多強，由中央複合體的柱狀神經元控制。'
         '第二個，Kain 等人 2012，同一實驗室：每隻果蠅的趨光程度不同，維持一生；血清素和 white 基因會壓低這種差異。'
         '第三個，Linneweber 2020 Science：視覺系統的 DCN 左右接線不對稱的程度因個體而異，越不對稱的果蠅，朝看到的物體走得越直；而且是因果關係：讓 DCN 不活動，這個關係就消失；人為增加不對稱，果蠅朝物體的表現就變好。'
         '結論：三篇都顯示這些差異不遺傳；Linneweber 直接證明差異來自發育時的隨機接線變化。基因（例如 Kain 的 white）可以調整差異的大小，但一隻果蠅會偏向哪一邊，不由基因決定。'
         '\n\n【備查，不用唸】\nLinneweber 的接線不對稱為何讓果蠅走得更直，報告未查到機制說明。')

# ---------- 8. 學自己 ----------
s = content_slide(prs, '果蠅能學會調整「自己產生的動作」', kicker='行為 5 · 操作式學習',
                  page=8, total=TOTAL, series=SERIES)
cols = [('學外界（world-learning）', '「某個圖案出現時，就會被熱到」', '腺苷酸環化酶（rutabaga）', DARK, WHITE),
        ('學自己（self-learning）', '「我往左轉，就會被熱到」\n沒有外界圖案可參考', 'PKC、FoxP\n（作用於運動神經元）', ACCENT, DARK)]
for i, (h, ex, mol, col, fc) in enumerate(cols):
    x = MARGIN + i * 4.0
    box(s, x, 1.65, 3.75, 3.6, fill=TINT)
    box(s, x, 1.65, 3.75, 0.7, fill=col)
    text(s, x + 0.1, 1.72, 3.55, 0.55, h, size=16, bold=True, color=fc, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, 2.5, 3.35, 1.3, ex, size=15, color=TEXT, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, 3.95, 3.35, 0.4, '需要的分子', size=12, color=MUTED, align=PP_ALIGN.CENTER)
    text(s, x + 0.2, 4.3, 3.35, 0.9, mol, size=15, bold=True, color=DARK, align=PP_ALIGN.CENTER)
items = [('1991', 'Wolf & Heisenberg：飛行模擬器中，果蠅學會避開會帶來熱的轉向方向'),
         ('2008', 'Brembs & Plendl：兩種學習用不同分子（雙重分離）'),
         ('2014', 'Mendoza 等人：FoxP 突變果蠅不能「學自己」，但能「學外界」'),
         ('2016', 'Colomb & Brembs：PKC 作用在運動神經元'),
         ('2024', 'Ehweiner 等人：翅膀轉向運動神經元中需要 aPKC（PKC 家族的一種）與 FoxP')]
for i, (yr, t) in enumerate(items):
    y = 1.7 + i * 0.75
    text(s, 8.65, y, 0.9, 0.5, yr, size=16, bold=True, color=ACCENT)
    text(s, 9.55, y, 3.2, 0.75, t, size=13, color=TEXT)
text(s, MARGIN, 5.55, W - 2 * MARGIN, 1.0,
     [[('連到定義：', {'bold': True, 'color': ACCENT}),
       ('先自己產生動作，再依結果選擇動作 = Brembs 的兩階段模型。果蠅 FoxP 與人類 FOXP2（學說話）同一家族', {})]], size=15)
notes(s, '第五個行為主題是操作式學習，也就是依照自己動作的結果來調整動作。在飛行模擬器裡，懲罰是一道熱光束。'
         '研究者分兩種：學外界，是學到「某個圖案出現就會被熱到」；學自己，是學到「我往左轉就會被熱到」，沒有外界圖案可以參考。'
         '1991 年 Wolf 和 Heisenberg 證明果蠅能學會避開帶來熱的轉向方向。'
         '2008 年 Brembs 發現兩種學習用不同分子，而且是雙重分離：rutabaga 腺苷酸環化酶突變只壞掉學外界，抑制 PKC 只壞掉學自己。'
         '2014 年 FoxP 突變的果蠅不能學自己但能學外界；2016 和 2024 年進一步定位到控制翅膀轉向的運動神經元。'
         '所以「學自己」至少有一部分發生在直接控制動作的神經元本身。'
         'Brembs 認為這是研究自由意志的好模型：先自己產生動作，再依結果選擇，正好是兩階段模型。'
         '\n\n【備查，不用唸】\n果蠅 FoxP 與人類 FOXP2 是同一基因家族、演化上相對應；FOXP2 與學說話有關，所以研究者認為兩者可能有共同分子基礎。')

# ---------- 9. 腦區 ----------
s = content_slide(prs, '自發行為的不同面向，對應到不同腦區', kicker='神經機制 1',
                  page=9, total=TOTAL, series=SERIES)
rows = [('中央複合體', '受損後開始走路的頻率正常，但每次走得比較短 → 讓走路持續', 'Martin、Raabe、Heisenberg 1999'),
        ('蕈狀體', '受損後在數小時觀察內總共走得比較多 → 平常抑制走路', 'Martin、Ernst、Heisenberg 1998'),
        ('橢圓體', '阻斷輸出 → 走與停的碎形模式消失', 'Martin、Faure、Ernst 2001'),
        ('中央複合體柱狀神經元', '控制左右轉偏好的強度', 'Buchanan 等人 2015'),
        ('蕈狀體與多巴胺', '讓部分蕈狀體不活動或改變多巴胺的量 → 活動「一陣一陣」的程度改變；多巴胺過高時較接近隨機', 'Sorribes 等人 2011')]
for i, (reg, res_, ref) in enumerate(rows):
    y = 1.65 + i * 0.98
    box(s, MARGIN, y, W - 2 * MARGIN, 0.85, fill=TINT if i % 2 == 0 else TINT2)
    text(s, MARGIN + 0.2, y + 0.18, 3.0, 0.5, reg, size=17, bold=True, color=DARK)
    text(s, MARGIN + 3.3, y + 0.18, 6.0, 0.6, res_, size=14, color=TEXT)
    text(s, W - MARGIN - 3.0, y + 0.22, 2.85, 0.45, ref, size=12, color=MUTED, align=PP_ALIGN.RIGHT)
notes(s, '神經機制的第一張，把目前知道的腦區整理成一張表。'
         '中央複合體受損的果蠅，開始走路的頻率正常，但每次走得比較短，所以它讓走路持續，而不是讓走路開始。'
         '蕈狀體相反，受損以後總共走得比較多，所以蕈狀體平常會抑制走路。'
         '橢圓體管走停時間的碎形模式；柱狀神經元管左右偏好的強度；最後一列是另一篇 Sorribes 2011：果蠅的活動常常是一段密集活動、接著長時間休息，這種一陣一陣的程度會因蕈狀體或多巴胺改變；多巴胺過高時，時間模式較沒有結構，也就是比較接近隨機。'
         '這些大多是 1998 到 2001 年 Heisenberg 實驗室的損傷實驗，解析度是腦區層級，還沒有到單一細胞型別。')

# ---------- 10. Libet + Tang ----------
s = content_slide(prs, '動作之前，腦中就有訊號；但訊號有兩種解釋', kicker='神經機制 2 · 準備電位',
                  page=10, total=TOTAL, series=SERIES)
box(s, MARGIN, 1.6, 6.0, 2.55, fill=TINT)
text(s, MARGIN + 0.2, 1.7, 5.6, 0.45, '人類：Libet 等人 1983', size=17, bold=True, color=DARK)
text(s, MARGIN + 0.2, 2.15, 5.6, 1.95,
     '受試者「覺得自己決定要動」之前約幾百毫秒，腦電圖就出現逐漸升高的「準備電位」。常被用來質疑自由意志。', size=14)
for i, (n, t, col, fc) in enumerate([('1', '決定已經做好', DARK, WHITE),
                                     ('2', '只是腦內波動在累積，越過門檻才動作；決定還沒做好（Schurger 等人 2012）', ACCENT, DARK)]):
    y = 4.35 + i * 1.05
    circle_num(s, MARGIN, y + 0.1, 0.6, n, fill=col, color=fc, size=15)
    text(s, MARGIN + 0.8, y + 0.05, 5.2, 0.95, t, size=14)
box(s, 7.0, 1.6, 5.7, 5.0, fill=TINT2)
text(s, 7.2, 1.7, 5.3, 0.45, '果蠅：Tang & Juusola 2010', size=17, bold=True, color=DARK)
text(s, 7.2, 2.2, 5.3, 4.3,
     [{'runs': '左右眼各看一個條紋畫面，兩者往相反方向移動；果蠅只能跟一邊轉，每 3–20 秒換一次邊', 'bullet': True},
      {'runs': '電極記錄左右視葉：約 20 毫秒就有反應，但與選哪邊無關；果蠅平均約 308 毫秒才第一次轉向（106 次，18 隻）', 'bullet': True},
      {'runs': '被選中那側的視葉活動變強，另一側變弱；畫面沒有改變（局部場電位：25/25 隻）', 'bullet': True},
      {'runs': '變化有一部分在換邊之前就開始 → 眼睛送進來的資訊被腦內活動「篩選」', 'bullet': True},
      {'runs': [('與兩種解釋的關係：', {'bold': True, 'color': ACCENT}), ('腦內活動在行為改變之前就變了；但作者說分不出是雜訊還是意圖', {})], 'bullet': True}],
     size=14, space_after=5)
notes(s, '接下來是「動作之前的訊號」。人類有名的 Libet 實驗：受試者覺得自己決定要動之前幾百毫秒，腦電圖就出現準備電位，常被用來說「腦比你先決定」。'
         '但 2012 年 Schurger 提出另一個解釋：準備電位可能只是隨機波動在累積，越過門檻那一刻才動作，在那之前波動也可能回落，所以決定還沒做好。'
         '記住這兩種解釋，下一張會用到。'
         '果蠅這邊，Tang 和 Juusola 2010：左右眼各看一個往相反方向移動的條紋，果蠅只能跟一邊，大約每 3 到 20 秒換邊。'
         '視葉 20 毫秒就有反應，但果蠅平均要 308 毫秒才第一次轉向，而且這個早期反應和果蠅何時、選哪邊對不上，所以跟選擇無關；真正有關的是之後幾秒內，被選中那一側的活動變強，而且有一部分在換邊之前就開始。'
         '用局部場電位分析，25 隻果蠅全部都有這個現象；論文不同的分析用了不同數量的果蠅，所以會看到 18 隻和 25 隻。作者說眼睛的資訊被腦內活動篩選。'
         '它跟上面兩種解釋的關係是：腦內活動在行為改變之前就變了，這是「動作之前的訊號」；但作者也承認，這個內部活動可能是雜訊、也可能是意圖，目前分不出是哪一種解釋。'
         '\n\n【備查，不用唸】\n論文各項分析用了不同數量的果蠅：18 隻是第一次轉向的等待時間，25 隻是局部場電位分析。')

# ---------- 11. Brezovec IPS ----------
s = content_slide(prs, 'IPS 在轉彎前 10 秒以上就出現左右差異，但預測力很弱', kicker='神經機制 3 · Brezovec 等人 2023（預印本）',
                  page=11, total=TOTAL, series=SERIES)
text(s, MARGIN, 1.6, W - 2 * MARGIN, 0.8,
     '9 隻雌果蠅，黑暗中在球上走，雙光子顯微鏡記錄全腦。左右差異＝同一腦區左右兩側螢光活動的差。',
     size=15)
nums = [('>10 秒', 'IPS（下後坡）左右差異出現；作者估約轉彎前 15 秒', DARK),
        ('約 3 秒', '其他腦區出現差異', MUTED),
        ('54%', '全部 3,786 次轉彎的預測準確率（亂猜 50%；p < 0.001）', ACCENT),
        ('66%', '只看轉彎前果蠅靜止不動的轉彎，共 54 次（p < 0.001）', ACCENT)]
for i, (n, l, col) in enumerate(nums):
    x = MARGIN + i * 3.05
    box(s, x, 2.45, 2.85, 2.35, fill=TINT)
    text(s, x + 0.1, 2.6, 2.65, 0.9, n, size=34, bold=True, color=col, align=PP_ALIGN.CENTER)
    text(s, x + 0.15, 3.55, 2.55, 1.2, l, size=13, color=TEXT, align=PP_ALIGN.CENTER)
box(s, MARGIN, 5.05, 6.0, 1.6, fill=TINT2)
text(s, MARGIN + 0.2, 5.12, 5.6, 1.5,
     [[('作者解讀：', {'bold': True, 'color': DARK}),
       ('訊號只能部分預測轉彎 → 那時可能還沒「決定好」，支持上一張的解釋 2；這個訊號像人類的準備電位', {})]],
     size=14)
text(s, 6.9, 5.12, 5.8, 1.5,
     [{'runs': [('限制：', {'bold': True, 'color': RED}), ('預印本，未經同行審查', {})], 'bullet': True},
      {'runs': '66% 只來自 54 次；只有 9 隻；果蠅固定、腦打開、在黑暗中', 'bullet': True},
      {'runs': '預測不準也可能來自量測限制', 'bullet': True}],
     size=14, space_after=3)
notes(s, '這是跟我們最相關的一篇：Clandinin 實驗室 2023 年的預印本。9 隻雌果蠅在黑暗中走球，雙光子記錄全腦。'
         '轉彎時腦的左右兩側活動不對稱，這不意外；意外的是 IPS，下後坡，作者叫它運動前中心，左右差異在轉彎前 10 秒以上就出現，作者估計大約 15 秒。其他腦區只在轉彎前約 3 秒。'
         '但用 IPS 預測轉彎方向，全部 3,786 次只猜對 54%，因為次數多所以統計上顯著；只看預測期間果蠅靜止的 54 次，猜對 66%。限定靜止是為了排除「訊號只是反映果蠅正在走」。'
         '作者的解讀是那時還沒決定好，比較支持上一張的第二種解釋。但這是作者的解讀，預測不準也可能是量測的限制。'
         'IPS 在我們的 LPU 分區裡也會出現，之後若要追這個訊號怎麼傳到轉向的下行神經元，可以從連結體下手。'
         '\n\n【備查，不用唸】\n另一篇 Aimon 等人 2023 eLife 用全腦影像比較自發與被迫走路：大部分腦區活動相似，但有些腦區只在自發走路時、在走路開始之前就變活躍。'
         '預測期間的確切長度，報告未查到。')

# ---------- 12. 決策 ----------
s = content_slide(prs, '有刺激時，果蠅的選擇也不是固定反射', kicker='神經機制 4 · 決策',
                  page=12, total=TOTAL, series=SERIES)
cards_row(s, 1.65, 4.95, [
    ('1', '權衡線索強弱', 'Zhang 等人 2007\n\n顏色與上下位置兩個線索把果蠅拉往相反方向；果蠅依相對強弱選擇避開哪個直條。\n\n需要蕈狀體與多巴胺', DARK),
    ('2', '累積證據', 'DasGupta 等人 2014\n\n氣味越難分辨，決定越慢、越容易錯，符合漂移—擴散模型。\n\nFoxP 突變較慢；只在蕈狀體 αβ 核心區 Kenyon 細胞降低 FoxP 也一樣', DARK),
    ('3', '細胞機制', 'Groschner 等人 2018\n\nFoxP 少 → 樹突上鉀離子通道 Shal（KV4）多 → 較慢到達放電門檻 → 決定較慢', DARK),
    ('4', '兩種逃跑', 'von Reyn 等人 2014\n\n同一種逼近黑影：巨纖維（giant fiber）早放電 → 短逃跑（快、不穩）；沒放電或較晚 → 長逃跑（慢、穩）', DARK),
], gap=0.2, head_size=16, body_size=13)
notes(s, '這四個實驗有外界刺激，所以不是純粹的自發行為，但它們說明果蠅的選擇不是固定反射。'
         '第一，Zhang 等人 2007 Science，郭愛克實驗室：訓練時某個顏色、某個上下位置的直條會帶來熱；測試時把兩個線索拆開，果蠅依相對強弱選擇，這需要蕈狀體和多巴胺。'
         '第二，DasGupta 等人 2014，Miesenböck 實驗室：氣味越難分辨，果蠅決定越慢、越容易錯，符合「累積證據到門檻」的漂移—擴散模型；關鍵在蕈狀體 αβ 核心區的 Kenyon 細胞和 FoxP。'
         '第三，Groschner 等人 2018，同一實驗室，找到細胞機制：FoxP 減少樹突上的 Shal 鉀通道；FoxP 少，Shal 就多，細胞較慢到達門檻，決定就慢。'
         '第四，von Reyn 等人 2014，Card 實驗室：同一種逼近的黑影，果蠅有時快但不穩地逃，有時慢但穩地逃，取決於巨纖維相對於其他平行迴路放電的時間。'
         '\n\n【備查，不用唸】\n黑影靠近越快，巨纖維越可能早放電，所以選擇有一部分取決於刺激細節。')

# ---------- 13. 小模型 ----------
s = content_slide(prs, '小模型：自發行為需要「腦內波動＋幾個會停留的活動狀態」', kicker='電腦模擬 1',
                  page=13, total=TOTAL, series=SERIES)
box(s, MARGIN, 1.6, 5.8, 5.0, fill=TINT)
text(s, MARGIN + 0.2, 1.7, 5.4, 0.45, '三個振盪器（Maye 等人 2007）', size=17, bold=True, color=DARK)
text(s, MARGIN + 0.2, 2.2, 5.4, 4.3,
     [{'runs': '三個互相連接、數值週期起伏的數學單元，輸出當作轉向力量；不對應真實神經元', 'bullet': True},
      {'runs': [('非線性結構：', {'bold': True}), ('輸出資料通過第 4 張的檢驗（非線性預測比直線預測準）', {})], 'bullet': True},
      {'runs': [('參數在穩定範圍：', {'bold': True}), ('外觀與果蠅扭力紀錄看不出差別，但沒有非線性結構', {})], 'bullet': True},
      {'runs': [('參數推過穩定界線：', {'bold': True}), ('有非線性結構，但外觀不像果蠅', {})], 'bullet': True},
      {'runs': [('結論：', {'bold': True, 'color': ACCENT}), ('這個模型解釋不了果蠅（兩個版本都不完全符合）。作者推論：真實的腦要在不穩定範圍運作，同時又產生像果蠅的輸出，所以比這個模型複雜；外觀相似 ≠ 機制相同', {})], 'bullet': True}],
     size=14, space_after=5)
box(s, 6.75, 1.6, 5.95, 5.0, fill=TINT2)
text(s, 6.95, 1.7, 5.55, 0.45, '小型遞迴網路（Maesani 等人 2015）', size=17, bold=True, color=DARK)
text(s, 6.95, 2.2, 5.55, 4.3,
     [{'runs': '資料：10 隻無刺激走路各 30 分鐘；約兩萬隻、98 個品系的氣味反應', 'bullet': True},
      {'runs': '1–5 個神經元；共 500 個候選模型（有／無波動 × 5 種大小 × 50）', 'bullet': True},
      {'runs': [('只有「網路＋波動」', {'bold': True}), ('重現走與停的時間分布；只有網路、或只有波動都較差', {})], 'bullet': True},
      {'runs': '2 個神經元就夠：網路活動有幾個傾向停留的狀態（例如「走」與「停」），波動讓活動越過門檻 → 自己開始走、自己停', 'bullet': True},
      {'runs': '氣味只改輸入、不改突觸強度，就改變這些狀態', 'bullet': True}],
     size=14, space_after=5)
notes(s, '接下來是電腦模擬，這部分是應要求加進來的。先說結論：目前沒有研究直接宣稱模擬了果蠅的自由意志，模擬的都是相關現象。'
         '左邊是 2007 年那篇行為論文附帶的小模型：三個振盪器。它的公式本身是非線性的。這裡的「非線性結構」是指輸出資料通過第 4 張那個檢驗，也就是非線性預測比直線預測準。'
         '參數在穩定範圍時，模型的數值會回到固定的起伏，輸出看起來跟果蠅一樣，但通不過這個檢驗；把參數推過穩定界線，數值不再回到固定起伏，輸出通過檢驗，但看起來不像果蠅。所以這個模型本身是失敗的；作者的推論是，真實果蠅的腦必須在不穩定範圍運作、同時又產生像果蠅的輸出，這個三振盪器做不到，所以腦比它複雜。'
         '作者的結論是外觀相似不代表機制相同，系統要在不穩定狀態下運作。'
         '右邊是 Maesani 等人 2015，Floreano、Benton 實驗室的小網路。資料有 10 隻果蠅無刺激時的走路，也有約兩萬隻果蠅的氣味反應，後者用來檢驗模型能不能也重現有刺激時的改變；他們共比較了 500 個候選模型。'
         '只要 2 個神經元加上隨機波動，就能重現果蠅走走停停的時間分布。'
         '關鍵是網路活動有幾個傾向停留的狀態，例如走和停，波動讓活動越過門檻，果蠅就自己開始走、自己停下。拿掉波動或拿掉網路都不行。'
         '注意左右兩邊的「穩定」不是同一件事：左邊講的是整個模型的參數範圍穩不穩定；右邊講的是活動會停留在哪幾個狀態。'
         '氣味只要改輸入就能改變行為，不用改接線，所以同一個網路能同時解釋有刺激和沒刺激的情況。'
         '\n\n【備查，不用唸】\n這兩個模型都不對應真實腦區。500 個候選模型不包含「只有波動、沒有網路」的對照組，那是另外比較的。')

# ---------- 14. 連結體模型 ----------
s = content_slide(prs, '連結體模型已經出現，但還沒有人讓它「自己產生行為」', kicker='電腦模擬 2',
                  page=14, total=TOTAL, series=SERIES)
hdr = ['研究', '模擬什麼', '真實接線', '連到行為']
rows = [('Churgin 等人 2025', '氣味偏好的個體差異（嗅葉 3,062 神經元）', 'hemibrain', '間接'),
        ('Shiu 等人 2024', '刺激引起的進食、理毛迴路（約 13.8 萬神經元）', 'FlyWire 全腦', '有，非自發'),
        ('Li 等人 2026（預印本）', '全腦自發活動；找出維持它的抑制性樞紐神經元', 'FlyWire 全腦', '沒有')]
xs = [MARGIN, 3.55, 9.05, 11.0]
ws = [2.9, 5.45, 1.9, 1.7]
box(s, MARGIN, 1.6, W - 2 * MARGIN, 0.55, fill=DARK)
for j, h_ in enumerate(hdr):
    text(s, xs[j] + 0.1, 1.67, ws[j], 0.45, h_, size=14, bold=True, color=WHITE)
for i, r in enumerate(rows):
    y = 2.2 + i * 0.85
    box(s, MARGIN, y, W - 2 * MARGIN, 0.78, fill=TINT if i % 2 == 0 else TINT2, radius=False)
    for j, c in enumerate(r):
        text(s, xs[j] + 0.1, y + 0.12, ws[j], 0.6, c, size=13, color=TEXT, bold=(j == 0))
text(s, MARGIN, 4.85, 3.4, 0.45, '還沒有研究同時做到：', size=16, bold=True, color=ACCENT)
gaps = ['用全腦連結體', '沒有刺激時自己產生行為', '和真實果蠅的自發行為比較\n（例如冪律、長程相關）']
for i, g in enumerate(gaps):
    x = MARGIN + i * 4.1
    circle_num(s, x, 5.4, 0.6, str(i + 1), fill=ACCENT, color=DARK, size=15)
    text(s, x + 0.75, 5.42, 3.2, 1.0, g, size=15, color=TEXT)
notes(s, '第二類是用真實接線的模型。'
         'Churgin 2025 用 hemibrain 接線做了 3,062 個神經元的嗅葉模型，隨機重新抽樣神經元和突觸來模擬發育差異；只有在嗅覺受器神經元到投射神經元這一段加隨機變化，個體差異的型態才跟真實果蠅一樣。模型本身不產生行為，所以跟行為的關係是間接的。'
         'Shiu 2024 Nature 是大家熟的 FlyWire 全腦 LIF 模型，預測進食和理毛迴路，但它是刺激驅動的。'
         'Li 2026 的預印本用 FlyWire 全腦模型重現自發活動，包括「神經元雪崩」：一群神經元的活動像連鎖反應擴散，雪崩大小沒有固定的典型值，也就是無尺度分布，和前面講的冪律同一類，'
         '並找到一小群抑制性樞紐神經元：把它們移除，全腦自發活動就停止；只保留它們和相關連接，就足以維持自發活動。但它只有腦活動，沒有行為。'
         '下面這三件事，目前還沒有研究同時做到。這可能就是我們的全腦模擬可以做的題目。'
         '\n\n【備查，不用唸】\n神經元雪崩：一群神經元的活動像連鎖反應擴散；雪崩大小沒有固定典型值（無尺度，與冪律同類）。')

# ---------- 15. 證明與未證明 ----------
s = content_slide(prs, '證明了「行為有一部分由腦自己產生」，沒有證明意識', kicker='這些研究證明了什麼',
                  page=15, total=TOTAL, series=SERIES)
box(s, MARGIN, 1.6, 5.9, 3.6, fill=TINT)
text(s, MARGIN + 0.2, 1.7, 5.5, 0.45, '已經有證據', size=18, bold=True, color=DARK)
text(s, MARGIN + 0.2, 2.2, 5.5, 3.0,
     [{'runs': '外界不變時仍自己產生行為，而且有結構', 'bullet': True},
      {'runs': '同樣刺激，依內部狀態做不同反應', 'bullet': True},
      {'runs': '動作前有訊號，能部分預測動作', 'bullet': True},
      {'runs': '中央複合體、橢圓體、蕈狀體、多巴胺有關', 'bullet': True},
      {'runs': '發育中的隨機接線造成個體差異', 'bullet': True},
      {'runs': '小模型：腦內波動＋幾個會停留的活動狀態即可', 'bullet': True}],
     size=14, space_after=3)
box(s, 6.8, 1.6, 5.9, 3.6, fill=TINT2)
text(s, 7.0, 1.7, 5.5, 0.45, '還沒有證據', size=18, bold=True, color=RED)
text(s, 7.0, 2.2, 5.5, 3.0,
     [{'runs': [('意識：', {'bold': True}), ('不能說明果蠅「感覺到」自己在決定', {})], 'bullet': True},
      {'runs': [('不受原因決定：', {'bold': True}), ('不能預測 ≠ 沒有原因。波動可能來自熱雜訊或量子層次的隨機性，也可能來自混沌（完全依規則、但不能長期預測）', {})], 'bullet': True},
      {'runs': [('道德責任：', {'bold': True}), ('哲學意義的自由意志，這些實驗不處理', {})], 'bullet': True}],
     size=14, space_after=4)
text(s, MARGIN, 5.4, W - 2 * MARGIN, 0.4, '主要爭議', size=16, bold=True, color=ACCENT)
text(s, MARGIN, 5.8, W - 2 * MARGIN, 1.0,
     [{'runs': '把「變異」叫「自由」只是改名字？Brembs：生物學基礎就是腦能產生變異，並控制變異的多少', 'bullet': True},
      {'runs': '隨機不等於自由 → 所以兩階段模型要有第二階段；準備電位與 IPS 訊號的兩種解釋，目前沒有實驗能分辨', 'bullet': True}],
     size=13, space_after=3)
notes(s, '整理一下。已經有證據的：果蠅在外界不變時自己產生有結構的行為；同樣刺激會依內部狀態不同而反應不同；動作前有可以部分預測的訊號；幾個腦區有關；發育中的隨機接線造成個體差異；小模型顯示波動加上多個穩定狀態就夠。'
         '沒有證據的：意識；「不受原因決定」，因為不能預測不等於沒有原因，混沌系統就是完全依規則運作、但不能長期預測；還有涉及道德責任的哲學意義。'
         '換句話說，行為的原因有一部分在腦內、不在外界，這和決定論可以並存。'
         '主要爭議有兩個：批評者說把變異叫自由只是改名字；Brembs 的回應是，自由意志的生物學基礎正是腦能自己產生變異，而且能調整變異的多少，這是可以量、可以找神經機制的性質。另外隨機本身不是自由，所以 Brembs 的模型一定要有第二階段的選擇。')

# ---------- 16. 結尾 ----------
s = dark_slide(prs)
text(s, MARGIN + 0.1, 0.7, 11, 0.4, '帶走三句話', size=16, color=ACCENT, bold=True)
take = ['外界不變時，果蠅仍會自己產生有規律的行為；腦內有隨機波動，但行為本身不是隨機雜訊',
        '腦在動作前 10 秒以上就有訊號（IPS），但只能稍微預測動作',
        '還沒有人用全腦連結體讓模型「自己產生行為」，再和真實果蠅比較']
for i, t in enumerate(take):
    y = 1.35 + i * 1.0
    circle_num(s, MARGIN + 0.1, y, 0.65, str(i + 1), fill=ACCENT, color=DARK, size=16)
    text(s, MARGIN + 1.0, y + 0.08, 11.2, 0.8, t, size=21, color=WHITE)
text(s, MARGIN + 0.1, 4.55, 11, 0.4, '未解的問題', size=16, color=ACCENT, bold=True)
text(s, MARGIN + 0.1, 5.0, 12, 2.0,
     [{'runs': '行為變異的源頭：少數特定神經元，還是全腦的網路性質？', 'bullet': True},
      {'runs': 'IPS 訊號是「決定的開始」還是「波動的累積」？它怎麼傳到控制轉向的下行神經元？', 'bullet': True},
      {'runs': '全腦模型能否重現自發轉向的冪律與長程相關？模型中必要的元件，在真實果蠅中是否也必要？', 'bullet': True}],
     size=16, color=LIGHT_ON_DARK, space_after=5)
notes(s, '最後帶走三句話。第一，果蠅在沒有刺激時仍會自己產生有規律的行為，不是雜訊。'
         '第二，腦在動作前 10 秒以上就有訊號，但只能稍微預測。'
         '第三，還沒有人用全腦連結體讓模型自己產生行為，再和真實果蠅比。'
         '下面這幾個未解問題，特別是 IPS 訊號怎麼傳到下行神經元、全腦模型能不能重現自發轉向，都是連結體加模擬可以接手的方向。謝謝。')

prs.save(OUT)
print('saved', os.path.abspath(OUT))
