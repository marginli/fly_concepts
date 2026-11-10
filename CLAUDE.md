# fly_concepts 果蠅概念圖庫

網址：https://marginli.github.io/fly_concepts/ （repo marginli/fly_concepts，公開；使用者同意什麼都可以放）

## 使用者怎麼用
工作中說「加一個條目：……」→ 做一頁、推上網。說「刪掉條目 X」→ `./remove_entry.sh <編號>`。沒刪的條目永久保留。

網頁刪除（2026-11-03）：每個條目頁底部有「刪除這個條目」連結，開預填標題「刪除條目 <編號>」的 issue；`.github/workflows/delete-entry.yml` 只對 marginli 開的 issue 動作（刪資料夾、build.py、推送、關 issue）。`rebuild.yml`：github.com 上直接改 entries/ 時自動重建。因為 GitHub 端會自己推送，`publish.sh` 一開始先 `git pull --rebase --autostash`；手動 git 操作前也要先 pull。

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
- 用語：antennal lobe 一律寫「嗅葉」、mushroom body 一律寫「蕈狀體」（不用觸角葉、蘑菇體）。
- 座標：A1 管線 µm 框（同 brain_division）。MaleCNS up=−y、front=−z。其他資料庫要加 loader 時先確認與哪個框對齊，不同框的東西不要放同一個 scene。
- 檔案大小：單一 scene.json 盡量 < 10 MB（骨架用 keep_every 抽點、mesh 限面數）；GitHub 單檔上限 100 MB。
- MaleCNS 標籤體積的 z 原點是 −191（不是管線框的 −175），flylib 的 LABEL_ORIGIN 已處理；判斷骨架點在哪區用 mcns_region_at()。說明裡寫的「經過哪區」要先用它核對。
- 參考物（全腦輪廓）用 `ref=True`，鏡頭取景不算它。
- three.js 由 jsdelivr 載入 three@0.160.0（importmap 在 build.py）。
- 點雲可逐點上色：`points_item(..., colors=N×3 RGB)`（viewer 用 vertexColors），例如突觸密度；範例 entries/20261103-pb-lpu-200/make.py。
- 3D 視窗右上角可加色條：`write_scene(..., legend={"title","colors","ticks","note"})`。縮放範圍與 near/far 由 viewer 依場景大小自動設（2026-11-03 修：原本縮太遠會超過 far 而全白）。
- 滾輪縮放由 viewer 自己處理：每次約 12%，200 毫秒內連續的滾輪事件只算一次（有些滑鼠／遠端桌面一格送多個事件）；另有「放大／縮小」按鈕。three.js 內建的會除以 (devicePixelRatio|0)，瀏覽器縮放 <100% 時一格到底（2026-11-03 修）。build.py 給 viewer.js、scene.json 加 ?v=<viewer 雜湊>，改 viewer 後瀏覽器會抓新版。

## 互動 DEMO 條目（meta.json 的 embed）
- `"embed": {"src": "demo.html", "height": N}` 用 iframe 嵌入；demo 若在 iframe 內 `parent.postMessage({demoH: 高度}, "*")`，條目頁會自動把 iframe 調成那個高度（範例見 `entries/20261110-six-actions/demo.html` 開頭的 script）。
- `"desc_wide": true`：下方說明欄和上方同寬（預設限 760px）。
- `"full_width": true`：整頁不限寬（預設 1100px），欄寬隨視窗大小變，DEMO 在 iframe 內也不限寬。
