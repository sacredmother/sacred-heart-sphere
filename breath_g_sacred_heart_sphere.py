
import datetime as dt
import json
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Breath G • Sacred Heart Sphere",
    page_icon="◉",
    layout="wide",
)

st.markdown('''
<style>
    .block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1500px;}
    h1, h2, h3 {letter-spacing: .02em;}
    [data-testid="stSidebar"] {background: linear-gradient(180deg,#080716,#11102b);}
    .love-card {
        border: 1px solid rgba(238,193,108,.28);
        border-radius: 18px;
        padding: 14px 18px;
        background: linear-gradient(135deg,rgba(15,12,40,.92),rgba(5,8,25,.92));
        box-shadow: 0 0 32px rgba(129,76,255,.08);
    }
</style>
''', unsafe_allow_html=True)

def digital_root(n: int) -> int:
    if n == 0:
        return 0
    return 1 + ((n - 1) % 9)

def digit_sum(n: int) -> int:
    return sum(int(ch) for ch in str(abs(n)))

def date_grammar(d: dt.date) -> dict:
    year_root = digital_root(digit_sum(d.year))
    month_root = digital_root(d.month)
    day_root = digital_root(digit_sum(d.day))
    raw_sum = year_root + month_root + day_root
    date_root = digital_root(raw_sum)
    pair_sum = month_root + day_root
    pair_root = digital_root(pair_sum)
    canon_pairs = {(4,5),(5,4),(6,3),(7,2),(8,1),(9,9)}
    return {
        "year_root": year_root,
        "month_root": month_root,
        "day_root": day_root,
        "date_root": date_root,
        "raw_sum": raw_sum,
        "pair_sum": pair_sum,
        "pair_root": pair_root,
        "is_gate": date_root == 1,
        "canon_pair": (month_root, day_root) in canon_pairs,
        "pair_label": f"{month_root}/{day_root}",
    }

st.title("Breath G • The Living Sacred Heart Sphere — v3")
st.caption("Zero-CDN version: native browser canvas only, designed to load reliably on Streamlit Cloud.")

with st.sidebar:
    st.header("Breathing Calendar")
    chosen_date = st.date_input("Date", value=dt.date.today())
    speed = st.slider("Breath speed", 0.15, 2.0, 0.72, 0.05)
    pov_count = st.slider("POV-eyes", 24, 240, 112, 8)
    memory_density = st.slider("Memory return", 0.1, 1.0, 0.68, 0.02)
    auto_orbit = st.toggle("Slow cosmic orbit", value=True)
    show_rays = st.toggle("Experience rays", value=True)
    show_words = st.toggle("Living words", value=True)
    st.divider()
    st.caption("Prototype 03 • Streamlit + native Canvas")

g = date_grammar(chosen_date)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Year • Field", g["year_root"])
c2.metric("Month • Octave", g["month_root"])
c3.metric("Day • Pulse", g["day_root"])
c4.metric("Date • Phase", g["date_root"])
c5.metric("Pair", g["pair_label"])

status = []
if g["is_gate"]:
    status.append("1-GATE OPEN")
if g["canon_pair"]:
    status.append("CANON OCTAVE PAIR")
if not status:
    status.append("LIVING PHASE")

st.markdown(
    f'''<div class="love-card"><b>{' • '.join(status)}</b><br>
    The selected date modulates the sphere without altering its unmoved center.
    Month/day pair sum: <b>{g['pair_sum']}</b> → root <b>{g['pair_root']}</b>.
    </div>''',
    unsafe_allow_html=True,
)

palettes = {
    1: ("#fff1b8", "#ffb347", "#ff5e7e"),
    2: ("#b7f7ff", "#43d9ff", "#4666ff"),
    3: ("#d8c2ff", "#9d68ff", "#ff62c8"),
    4: ("#ffd6a0", "#ff8b4a", "#ffdc64"),
    5: ("#c3ffcb", "#55e6a5", "#35a6ff"),
    6: ("#f6bdff", "#e36cff", "#7957ff"),
    7: ("#b9e9ff", "#688cff", "#b570ff"),
    8: ("#ffd3df", "#ff5e91", "#ff9f43"),
    9: ("#ffffff", "#8ef6ff", "#ffdb70"),
}

config = {
    "dateLabel": chosen_date.strftime("%B %d, %Y"),
    "yearRoot": g["year_root"],
    "monthRoot": g["month_root"],
    "dayRoot": g["day_root"],
    "dateRoot": g["date_root"],
    "pairLabel": g["pair_label"],
    "gate": g["is_gate"],
    "canonPair": g["canon_pair"],
    "speed": speed,
    "povCount": pov_count,
    "memoryDensity": memory_density,
    "autoOrbit": auto_orbit,
    "showRays": show_rays,
    "showWords": show_words,
    "palette": palettes[g["date_root"]],
}

html = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
html, body {
  margin:0;
  padding:0;
  overflow:hidden;
  background:#02030d;
  font-family: Georgia, serif;
}
#wrap {
  position:relative;
  width:100%;
  height:790px;
  border-radius:24px;
  overflow:hidden;
  background:
    radial-gradient(circle at 50% 45%, rgba(38,28,90,.95), rgba(6,7,22,.98) 45%, #000 100%);
  box-shadow: inset 0 0 80px rgba(126,104,255,.16), 0 0 35px rgba(0,0,0,.4);
}
canvas {
  width:100%;
  height:100%;
  display:block;
}
#hud {
  position:absolute;
  left:28px;
  top:22px;
  z-index:5;
  pointer-events:none;
  color:white;
  text-shadow:0 2px 18px #000;
}
.kicker {
  font-family:Arial,sans-serif;
  letter-spacing:.24em;
  font-size:11px;
  color:#efca7a;
}
.title {
  font-size:30px;
  margin-top:8px;
  color:#fff5d8;
}
.meta {
  font-family:Arial,sans-serif;
  margin-top:7px;
  color:#d9d8f2;
  font-size:13px;
}
.badge {
  display:inline-block;
  border:1px solid rgba(255,211,115,.55);
  padding:5px 10px;
  border-radius:999px;
  font-family:Arial,sans-serif;
  font-size:10px;
  letter-spacing:.15em;
  color:#ffe9ad;
  margin-top:10px;
  background:rgba(20,12,48,.55);
}
#truth {
  position:absolute;
  bottom:24px;
  left:50%;
  transform:translateX(-50%);
  z-index:5;
  width:min(88%,1000px);
  text-align:center;
  pointer-events:none;
  text-shadow:0 2px 18px #000;
}
#truth .line1 {
  font-size:22px;
  color:#fff0c5;
  letter-spacing:.04em;
}
#truth .line2 {
  font-family:Arial,sans-serif;
  font-size:12px;
  color:#c6c5df;
  margin-top:7px;
  letter-spacing:.11em;
}
#hint {
  position:absolute;
  right:20px;
  bottom:18px;
  z-index:5;
  font:11px Arial,sans-serif;
  color:#777b9d;
}
</style>
</head>
<body>
<div id="wrap">
  <canvas id="c"></canvas>
  <div id="hud">
    <div class="kicker">BREATH G • LIVING CALENDAR</div>
    <div class="title" id="dateLabel"></div>
    <div class="meta" id="meta"></div>
    <div id="badges"></div>
  </div>
  <div id="truth">
    <div class="line1">Wholeness does not become more whole.</div>
    <div class="line2">THE CENTER REMAINS INFINITE • THE HORIZON OF RELATIONSHIP MOVES</div>
  </div>
  <div id="hint">drag to turn • native canvas</div>
</div>

<script>
const CFG = __CONFIG__;
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
const wrap = document.getElementById("wrap");

document.getElementById("dateLabel").textContent = CFG.dateLabel;
document.getElementById("meta").textContent =
  `FIELD ${CFG.yearRoot} • OCTAVE ${CFG.monthRoot} • PULSE ${CFG.dayRoot} • PHASE ${CFG.dateRoot} • PAIR ${CFG.pairLabel}`;
let badges = [];
if (CFG.gate) badges.push("1-GATE OPEN");
if (CFG.canonPair) badges.push("CANON PAIR");
document.getElementById("badges").innerHTML = badges.map(b => `<span class="badge">${b}</span>`).join(" ");

let W = 1, H = 1, DPR = 1;
function resize() {
  DPR = Math.min(window.devicePixelRatio || 1, 2);
  W = wrap.clientWidth;
  H = wrap.clientHeight;
  canvas.width = Math.floor(W * DPR);
  canvas.height = Math.floor(H * DPR);
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
resize();
window.addEventListener("resize", resize);

function hexToRgb(hex) {
  hex = hex.replace("#","");
  return {
    r: parseInt(hex.slice(0,2),16),
    g: parseInt(hex.slice(2,4),16),
    b: parseInt(hex.slice(4,6),16)
  };
}
function rgba(hex, a) {
  const c = hexToRgb(hex);
  return `rgba(${c.r},${c.g},${c.b},${a})`;
}
const P = CFG.palette;

function rand(seed) {
  let x = Math.sin(seed) * 10000;
  return x - Math.floor(x);
}

const golden = Math.PI * (3 - Math.sqrt(5));
let eyes = [];
for (let i=0; i<CFG.povCount; i++) {
  const y = 1 - (i / Math.max(1, CFG.povCount-1)) * 2;
  const r = Math.sqrt(Math.max(0, 1-y*y));
  const a = golden * i;
  eyes.push({
    x: Math.cos(a) * r,
    y: y,
    z: Math.sin(a) * r,
    phase: rand(i*17.17) * Math.PI * 2,
    tone: i % 3
  });
}

let memories = [];
const memN = Math.floor(650 * CFG.memoryDensity);
for (let i=0; i<memN; i++) {
  const rr = Math.pow(rand(i*9.91), .55);
  const y = 1 - rand(i*6.31) * 2;
  const ar = Math.sqrt(Math.max(0, 1-y*y));
  const a = rand(i*4.77) * Math.PI * 2;
  memories.push({
    x: Math.cos(a)*ar*rr,
    y: y*rr,
    z: Math.sin(a)*ar*rr,
    s: 1 + rand(i*3.13)*3,
    phase: rand(i*11.1) * Math.PI * 2,
    tone: i % 3
  });
}

let stars = [];
for (let i=0; i<900; i++) {
  stars.push({
    x: rand(i*2.1),
    y: rand(i*3.7),
    s: .4 + rand(i*8.3)*1.8,
    a: .15 + rand(i*5.8)*.75,
    p: rand(i*4.4)*Math.PI*2
  });
}

let rotX = .18, rotY = 0, targetX = .18, targetY = 0;
let dragging = false, lx = 0, ly = 0;
canvas.addEventListener("pointerdown", e => { dragging=true; lx=e.clientX; ly=e.clientY; });
window.addEventListener("pointerup", () => dragging=false);
window.addEventListener("pointermove", e => {
  if (!dragging) return;
  targetY += (e.clientX - lx) * .008;
  targetX += (e.clientY - ly) * .008;
  lx = e.clientX; ly = e.clientY;
});

function rotate(p, ax, ay) {
  let x=p.x, y=p.y, z=p.z;
  let cy=Math.cos(ay), sy=Math.sin(ay);
  let x1=x*cy + z*sy;
  let z1=-x*sy + z*cy;
  let cx=Math.cos(ax), sx=Math.sin(ax);
  let y1=y*cx - z1*sx;
  let z2=y*sx + z1*cx;
  return {x:x1,y:y1,z:z2};
}
function project(p, cx, cy, R) {
  const persp = 1.9 / (2.55 - p.z);
  return {
    x: cx + p.x * R * persp,
    y: cy + p.y * R * persp,
    s: persp,
    z: p.z
  };
}
function glowCircle(x,y,r,color,a) {
  const g = ctx.createRadialGradient(x,y,0,x,y,r);
  g.addColorStop(0, rgba(color,a));
  g.addColorStop(.25, rgba(color,a*.45));
  g.addColorStop(1, rgba(color,0));
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x,y,r,0,Math.PI*2);
  ctx.fill();
}
function strokeCircle(x,y,r,color,a,w=1) {
  ctx.strokeStyle = rgba(color,a);
  ctx.lineWidth = w;
  ctx.beginPath();
  ctx.arc(x,y,r,0,Math.PI*2);
  ctx.stroke();
}
function lineGlow(x1,y1,x2,y2,color,a,w=1) {
  ctx.strokeStyle = rgba(color,a);
  ctx.lineWidth = w;
  ctx.beginPath();
  ctx.moveTo(x1,y1);
  ctx.lineTo(x2,y2);
  ctx.stroke();
}

let start = performance.now();
function draw(now) {
  requestAnimationFrame(draw);
  const t = (now - start) / 1000;
  rotX += (targetX - rotX) * .04;
  rotY += (targetY - rotY) * .04;
  if (CFG.autoOrbit) targetY += .0018;

  const cx = W/2;
  const cy = H/2 + 22;
  const baseR = Math.min(W, H) * .285;
  const breath = (Math.sin(t * CFG.speed) + 1) / 2;
  const R = baseR * (1 + breath*.055 + (CFG.gate ? .025 : 0));

  ctx.clearRect(0,0,W,H);

  const bg = ctx.createRadialGradient(cx,cy,0,cx,cy,Math.max(W,H)*.7);
  bg.addColorStop(0, "rgba(44,34,112,.34)");
  bg.addColorStop(.45, "rgba(10,9,35,.55)");
  bg.addColorStop(1, "rgba(0,0,0,1)");
  ctx.fillStyle = bg;
  ctx.fillRect(0,0,W,H);

  for (const s of stars) {
    const a = s.a * (.55 + .45*Math.sin(t*.7+s.p));
    ctx.fillStyle = `rgba(210,220,255,${a})`;
    ctx.beginPath();
    ctx.arc(s.x*W, s.y*H, s.s, 0, Math.PI*2);
    ctx.fill();
  }

  glowCircle(cx, cy, R*1.55, P[2], .15 + breath*.10);
  glowCircle(cx, cy, R*1.10, P[1], .12 + breath*.12);

  ctx.save();
  ctx.translate(cx,cy);
  ctx.rotate(rotY*.3);
  for (let i=0; i<15; i++) {
    ctx.strokeStyle = rgba(i%2?P[0]:P[1], .04 + i*.002);
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.ellipse(0,0,R*(1.04+i*.012),R*(.35+i*.014),rotX+i*.37,0,Math.PI*2);
    ctx.stroke();
  }
  ctx.restore();

  strokeCircle(cx,cy,R,P[0],.75,1.4);
  strokeCircle(cx,cy,R*1.01,P[1],.35,1);
  strokeCircle(cx,cy,R*.985,P[2],.25,1);

  const shellGrad = ctx.createRadialGradient(cx-R*.25,cy-R*.35,R*.05,cx,cy,R*1.1);
  shellGrad.addColorStop(0, rgba(P[0],.18));
  shellGrad.addColorStop(.5, rgba(P[1],.055));
  shellGrad.addColorStop(1, rgba(P[2],.12));
  ctx.fillStyle = shellGrad;
  ctx.beginPath();
  ctx.arc(cx,cy,R,0,Math.PI*2);
  ctx.fill();

  glowCircle(cx,cy,R*.36,P[0],.50 + breath*.25);
  strokeCircle(cx,cy,R*.18,P[0],.55,1);
  strokeCircle(cx,cy,R*.27,P[1],.28,1);
  for (let k=0;k<12;k++) {
    const a = t*.04 + k*Math.PI/6;
    lineGlow(cx,cy,cx+Math.cos(a)*R*.32,cy+Math.sin(a)*R*.32,P[k%2?1:0],.20,1);
  }

  const projectedMem = memories.map(m => {
    const pr = rotate(m, rotX*.85 + t*.015, rotY*.85 + t*.02);
    return {...project(pr,cx,cy,R*.77), tone:m.tone, phase:m.phase, size:m.s};
  }).sort((a,b)=>a.z-b.z);

  for (const m of projectedMem) {
    const color = P[m.tone];
    const a = (.16 + .28*(m.z+1)/2) * (.6 + .4*Math.sin(t*1.2+m.phase));
    glowCircle(m.x,m.y,m.size*5*m.s,color,a*.55);
    ctx.fillStyle = rgba(color, a+.12);
    ctx.beginPath();
    ctx.arc(m.x,m.y,m.size*m.s,0,Math.PI*2);
    ctx.fill();
  }

  const projectedEyes = eyes.map((e, idx) => {
    const pr = rotate(e, rotX, rotY);
    return {...project(pr,cx,cy,R), source:e, idx};
  }).sort((a,b)=>a.z-b.z);

  if (CFG.showRays) {
    for (const e of projectedEyes) {
      if (e.idx % 3 !== 0 || e.z < -0.25) continue;
      const color = P[e.source.tone];
      const a = .10 + .22*(e.z+1)/2;
      const dx = (e.x - cx), dy = (e.y - cy);
      const len = Math.sqrt(dx*dx+dy*dy) || 1;
      const ox = e.x + dx/len * R*.32;
      const oy = e.y + dy/len * R*.32;
      lineGlow(ox,oy,e.x,e.y,color,a,1.2);
      lineGlow(e.x,e.y,cx,cy,color,a*.32,.8);
    }
  }

  for (const e of projectedEyes) {
    const front = (e.z+1)/2;
    const color = P[e.source.tone];
    const blink = .48 + .52*Math.pow((Math.sin(t*.9+e.source.phase)+1)/2, 2);
    const rw = Math.max(2.5, 7.5*e.s*(.7+front*.7));
    const rh = rw * (.43 + .25*blink);
    const alpha = .25 + front*.70;

    ctx.save();
    ctx.translate(e.x,e.y);
    ctx.rotate(Math.atan2(e.source.y, e.source.x) + rotY*.4);
    glowCircle(0,0,rw*2.6,color,alpha*.23);
    ctx.strokeStyle = rgba(color,alpha);
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.ellipse(0,0,rw,rh,0,0,Math.PI*2);
    ctx.stroke();
    ctx.fillStyle = "rgba(4,3,15,.78)";
    ctx.beginPath();
    ctx.arc(0,0,Math.max(1.4,rw*.22),0,Math.PI*2);
    ctx.fill();
    ctx.restore();
  }

  glowCircle(cx,cy,34 + breath*20,P[0],.85);
  ctx.fillStyle = rgba(P[0],.95);
  ctx.beginPath();
  ctx.arc(cx,cy,5.5 + breath*2,0,Math.PI*2);
  ctx.fill();

  if (CFG.showWords) {
    ctx.font = "15px Georgia";
    ctx.fillStyle = "rgba(255,240,197,.86)";
    ctx.textAlign = "center";
    ctx.fillText("infinite center", cx, cy - R*.47);
    ctx.fillText("living horizon", cx, cy + R*.49);
    ctx.font = "12px Arial";
    ctx.fillStyle = "rgba(218,216,244,.68)";
    ctx.fillText("each eye returns one irreplaceable color of self-knowing", cx, cy + R*.57);
  }
}
requestAnimationFrame(draw);
</script>
</body>
</html>
'''.replace("__CONFIG__", json.dumps(config))

components.html(html, height=810, scrolling=False)

with st.expander("Why this version exists"):
    st.markdown('''
The earlier prototype used Three.js from an external CDN. Your deployed app reported that Three.js did not load, which means the external script was blocked or unavailable in that environment.

This v3 version uses only native browser canvas. It does not depend on any outside JavaScript library, so it should render reliably inside Streamlit Cloud.
    ''')

with st.expander("What this prototype is expressing"):
    st.markdown('''
- **The center never travels.** Its pulse changes visibility, not essence.
- **The circumference breathes.** Expansion represents an enlarging horizon of possible relationship.
- **POV-eyes awaken asynchronously.** No perspective is duplicated or expendable.
- **Experience rays return inward.** Life goes outward; memory and meaning return to the common interior.
- **The interior becomes richer without becoming closed.**
- **The Breathing Calendar modulates the display.** Date roots influence palette, rhythm, activation, and gate emphasis.
    ''')

