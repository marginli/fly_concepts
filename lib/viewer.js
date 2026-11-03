// fly_concepts 共用 3D 檢視器：讀 scene.json（格式見 lib/flylib.py），畫腦區外形、神經元骨架、點雲。
// 用法：<div id="view"></div><div id="panel"></div>
//       <script type="module">import {mount} from "../../lib/viewer.js"; mount("scene.json");</script>
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export async function mount(url, opts = {}) {
  const host = document.getElementById(opts.view || "view");
  const panel = document.getElementById(opts.panel || "panel");
  const scene = await (await fetch(url)).json();

  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  host.appendChild(renderer.domElement);
  const s3 = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(35, 1, 1, 20000);
  const ctl = new OrbitControls(cam, renderer.domElement);
  ctl.enableDamping = true;
  s3.add(new THREE.AmbientLight(0xffffff, 0.7));
  const dl = new THREE.DirectionalLight(0xffffff, 0.8);
  s3.add(dl);

  const box = new THREE.Box3();
  const objs = [];
  for (const g of scene.groups) {
    g._objs = [];
    for (const it of g.items) {
      let o;
      if (it.kind === "mesh") {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(it.v, 3));
        geo.setIndex(it.f);
        geo.computeVertexNormals();
        o = new THREE.Mesh(geo, new THREE.MeshLambertMaterial({
          color: it.color, transparent: it.opacity < 1, opacity: it.opacity,
          depthWrite: it.opacity >= 0.6, side: THREE.DoubleSide }));
      } else if (it.kind === "lines") {
        const pos = [];
        for (const s of it.seg) for (let k = 0; k + 5 < s.length; k += 3) pos.push(s[k], s[k + 1], s[k + 2], s[k + 3], s[k + 4], s[k + 5]);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
        o = new THREE.LineSegments(geo, new THREE.LineBasicMaterial({ color: it.color }));
      } else if (it.kind === "points") {
        const geo = new THREE.BufferGeometry();
        geo.setAttribute("position", new THREE.Float32BufferAttribute(it.p, 3));
        // it.c（選用）：每點一組 RGB（0–1），例如依數值上色的點雲；沒有就整組用 it.color
        if (it.c) geo.setAttribute("color", new THREE.Float32BufferAttribute(it.c, 3));
        o = new THREE.Points(geo, new THREE.PointsMaterial({ color: it.c ? 0xffffff : it.color, vertexColors: !!it.c,
          size: it.size, sizeAttenuation: true, transparent: it.opacity !== undefined, opacity: it.opacity ?? 1 }));
      }
      if (!o) continue;
      o.visible = it.visible !== false;
      o.geometry.computeBoundingBox();
      if (!it.ref) box.union(o.geometry.boundingBox);  // ref＝參考物（全腦輪廓等），不參與鏡頭取景
      if (it.ref) o.renderOrder = -1;
      s3.add(o); objs.push(o); g._objs.push([it, o]);
    }
  }

  
  if (box.isEmpty()) for (const o of objs) box.union(o.geometry.boundingBox);
  const center = box.getCenter(new THREE.Vector3());
  const radius = box.getSize(new THREE.Vector3()).length() / 2 || 100;
  // 縮放範圍與可視距離跟著場景大小走：避免縮太遠超過最遠可視距離（畫面變空白）或鑽進物體裡
  ctl.minDistance = radius * 0.35;
  ctl.maxDistance = radius * 12;
  ctl.zoomSpeed = 0.6;
  cam.near = radius / 300;
  cam.far = radius * 40;
  cam.updateProjectionMatrix();
  const up = new THREE.Vector3(...(scene.up || [0, 1, 0]));
  const front = new THREE.Vector3(...(scene.front || [0, 0, 1]));
  const side = new THREE.Vector3().crossVectors(up, front);
  function look(dir, upv) {
    cam.position.copy(center).addScaledVector(dir.clone().normalize(), radius * 3.2);
    cam.up.copy(upv);
    ctl.target.copy(center);
    cam.lookAt(center);
    ctl.update();
  }
  const views = { "正面": () => look(front, up), "側面": () => look(side, up), "上面": () => look(up, front.clone().negate()) };
  views["正面"]();

  function resize() {
    const w = host.clientWidth, h = host.clientHeight;
    renderer.setSize(w, h); cam.aspect = w / h; cam.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(host); resize();
  (function tick() { requestAnimationFrame(tick); ctl.update(); dl.position.copy(cam.position); renderer.render(s3, cam); })();

  // 色條（scene.legend，選用）：{title, colors:[hex…由低到高], ticks:[[位置0–1, 標籤]…], note}
  if (scene.legend) {
    const L = scene.legend;
    host.style.position = "relative";
    const box2 = document.createElement("div");
    box2.style.cssText = "position:absolute;right:10px;top:10px;background:rgba(255,255,255,.85);border-radius:6px;padding:6px 8px;font-size:12px;line-height:1.3;color:#222;pointer-events:none;max-width:170px";
    const grad = `linear-gradient(to top, ${L.colors.map((c, i) => `${c} ${(100 * i / (L.colors.length - 1)).toFixed(1)}%`).join(",")})`;
    let ticks = "";
    for (const [pos, lab] of L.ticks || []) ticks += `<div style="position:absolute;left:22px;bottom:${(pos * 100).toFixed(1)}%;transform:translateY(50%);white-space:nowrap">— ${lab}</div>`;
    box2.innerHTML = `<div style="font-weight:600;margin-bottom:4px">${L.title}</div>
      <div style="position:relative;height:150px;width:110px"><div style="position:absolute;left:0;top:0;bottom:0;width:16px;background:${grad};border:1px solid #888"></div>${ticks}</div>
      ${L.note ? `<div style="margin-top:4px;color:#555">${L.note}</div>` : ""}`;
    host.appendChild(box2);
  }

  // 控制面板：視角按鈕＋每組、每項的勾選
  if (panel) {
    const bar = document.createElement("div"); bar.className = "views";
    for (const [k, f] of Object.entries(views)) {
      const b = document.createElement("button"); b.textContent = k; b.onclick = f; bar.appendChild(b);
    }
    panel.appendChild(bar);
    for (const g of scene.groups) {
      const d = document.createElement("details"); d.open = g.items.length <= 12;
      const sm = document.createElement("summary");
      const gc = document.createElement("input"); gc.type = "checkbox";
      gc.checked = g._objs.some(([, o]) => o.visible);
      gc.onclick = (e) => { e.stopPropagation(); for (const [, o] of g._objs) o.visible = gc.checked; d.querySelectorAll("li input").forEach((c) => (c.checked = gc.checked)); };
      sm.append(gc, " " + g.name); d.appendChild(sm);
      const ul = document.createElement("ul");
      for (const [it, o] of g._objs) {
        const li = document.createElement("li"); const lb = document.createElement("label");
        const c = document.createElement("input"); c.type = "checkbox"; c.checked = o.visible;
        c.onchange = () => (o.visible = c.checked);
        const sw = document.createElement("span"); sw.className = "sw"; sw.style.background = it.color;
        lb.append(c, sw, " " + it.name); li.appendChild(lb); ul.appendChild(li);
      }
      d.appendChild(ul); panel.appendChild(d);
    }
  }
}
