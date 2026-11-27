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
- 回報高度**不可用 `document.documentElement.scrollHeight`**：它至少等於 iframe 目前高度，外層又加 4 px，兩邊互相觸發 resize，框會一直變長（2026-11-20 otf-learning 踩過）。要量內容容器的底（例：`.wrap.getBoundingClientRect().bottom`＋body 邊距），且高度沒變就不送。
- `"desc_wide": true`：下方說明欄和上方同寬（預設限 760px）。
- `"full_width": true`：整頁不限寬（預設 1100px），欄寬隨視窗大小變，DEMO 在 iframe 內也不限寬。
- `"desc_collapse": true`：說明欄除第一節外，每節包成可收合的 details（預設收合）。

## 神經元畫板（entries/20261127-neuron-board，2026-11-27）
使用者說「畫某某神經元」「在畫板加……」→ 不另開條目，在畫板加一個畫面：
1. 確認資料集（mcns／fw／banc，沒說就問）。
2. `cd entries/20261127-neuron-board && python3 draw.py --ds fw --neurons "MBON01,MBON02" --side R [--max-per-type 5] [--regions auto|none|A,B] [--title …] [--id …] [--note …]`。產生 `views/<id>.json` 並加到 `views.json` 最前面；`--remove <id>` 刪畫面。
3. `python3 build.py`、本機截圖看一下、`./publish.sh "neuron-board: add <id>"`。
- 共用讀取工具 `lib/flyds.py`：三份資料的腦區標籤、註記（型別→編號）、骨架、腦區外形（快取在 `~/.cache/fly_concepts`）。
- 座標各自獨立：mcns 上 −y 前 −z；fw（FC12 框，標籤用 thre/t8 加寬版）上 +y 前 +z，左右與另兩份相反；banc（原生 µm）上 +z 前 −y（11-27 用萼／葉／嗅葉／GNG 重心確認；先前寫的 −y／−z 是錯的）。
- MaleCNS 只有腦 80 區（沒有腹神經索標籤）；BANC 有腦 75＋腹神經索 26 區。
- 骨架點數全部合計上限 15 萬（draw.py 的 MAX_PTS），APL 單顆畫面約 0.5–1.7 MB。
- 突觸：`--show fibre,pre,post`（syn＝pre,post；預設 fibre）。pre＝輸出點紅、post＝輸入點藍（固定色），有畫突觸時纖維改用不含紅藍的色盤。合計上限 12 萬點（MAX_SYN，超過隨機抽樣，表上列全部數量）。APL 纖維＋突觸約 3.5 MB。
- 突觸索引 `lib/build_syn_index.py` 建在 /mnt/sda1/work1/fly_concepts_syn/<ds>/（依神經元排序；mcns 由 syn-points 換管線框、fw 由 syn_w5 用 t1 仿射、banc 由 parquet ×(16,16,45) nm）；讀取 `flyds.synapses(ds, id, end)`。fw、banc 的 pre 原始是一個連結一列，讀取時同位置去重。
