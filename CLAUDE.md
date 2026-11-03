# fly_concepts 果蠅概念圖庫

網址：https://marginli.github.io/fly_concepts/ （repo marginli/fly_concepts，公開；使用者同意什麼都可以放）

## 使用者怎麼用
工作中說「加一個條目：……」→ 做一頁、推上網。說「刪掉條目 X」→ `./remove_entry.sh <編號>`。沒刪的條目永久保留。

## 加條目流程
1. 問清楚（或從要求判斷）要用哪一份資料：**每次都要指定**（MaleCNS／FlyWire／hemibrain／BANC），使用者沒說就問。
2. 建 `entries/YYYYMMDD-<英文短名>/`，內含：
   - `make.py`：產生 scene.json（3D）或 png（平面圖）；共用工具在 `lib/flylib.py`（MaleCNS 腦區外形、骨架、scene 格式）。參考 `entries/20261103-mb-kc/make.py`。
   - `meta.json`：title、date、dataset、tags、summary、scene（有 3D）、figs（有平面圖）。格式見 build.py 開頭。
   - `desc.html`：白話短說明（半頁內），外行讀得懂。
3. 說明文字交付前跑 cold-read skill：一個新冷讀者、一到兩輪，到沒有「看不懂」。
4. 本機測試：`python3 -m http.server` ＋ playwright（`executable_path=/usr/bin/google-chrome`、headless=False、DISPLAY=:20、swiftshader）截圖看 3D 有沒有出來。
5. `./publish.sh "add <編號>"`。GitHub Pages 約 1–2 分鐘後更新。

## 注意
- 座標：A1 管線 µm 框（同 brain_division）。MaleCNS up=−y、front=−z。其他資料庫要加 loader 時先確認與哪個框對齊，不同框的東西不要放同一個 scene。
- 檔案大小：單一 scene.json 盡量 < 10 MB（骨架用 keep_every 抽點、mesh 限面數）；GitHub 單檔上限 100 MB。
- 參考物（全腦輪廓）用 `ref=True`，鏡頭取景不算它。
- three.js 由 jsdelivr 載入 three@0.160.0（importmap 在 build.py）。
