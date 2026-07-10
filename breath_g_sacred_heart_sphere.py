
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
    is_gate = date_root == 1
    canon_pairs = {(4,5),(5,4),(6,3),(7,2),(8,1),(9,9)}
    return {
        "year_root": year_root,
        "month_root": month_root,
        "day_root": day_root,
        "date_root": date_root,
        "raw_sum": raw_sum,
        "pair_sum": pair_sum,
        "pair_root": pair_root,
        "is_gate": is_gate,
        "canon_pair": (month_root, day_root) in canon_pairs,
        "pair_label": f"{month_root}/{day_root}",
    }

st.title("Breath G • The Living Sacred Heart Sphere")
st.caption("Wholeness remains whole. Relationship deepens its experienced richness.")

with st.sidebar:
    st.header("Breathing Calendar")
    chosen_date = st.date_input("Date", value=dt.date.today())
    speed = st.slider("Breath speed", 0.15, 2.0, 0.65, 0.05)
    pov_count = st.slider("POV-eyes", 24, 240, 96, 8)
    memory_density = st.slider("Memory return", 0.1, 1.0, 0.68, 0.02)
    auto_orbit = st.toggle("Slow cosmic orbit", value=True)
    show_rays = st.toggle("Experience rays", value=True)
    show_labels = st.toggle("Living words", value=True)
    st.divider()
    st.caption("Prototype 01 • Streamlit + Three.js")

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
p = palettes[g["date_root"]]

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
    "showLabels": show_labels,
    "palette": p,
}

html = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<style>
html,body{margin:0;height:100%;overflow:hidden;background:
radial-gradient(circle at 50% 45%,#151044 0%,#070716 38%,#01030d 78%,#000 100%);
font-family:Georgia,serif;color:white}
#stage{position:relative;width:100%;height:780px;overflow:hidden;border-radius:24px;
box-shadow:inset 0 0 80px rgba(100,80,255,.12),0 0 40px rgba(0,0,0,.35)}
#hud{position:absolute;left:28px;top:22px;z-index:4;pointer-events:none;text-shadow:0 2px 18px #000}
.kicker{font-family:Arial,sans-serif;letter-spacing:.24em;font-size:11px;color:#efca7a}
.title{font-size:28px;margin-top:7px;color:#fff5d8}
.meta{font-family:Arial,sans-serif;margin-top:7px;color:#c9c8e8;font-size:13px}
#truth{position:absolute;bottom:22px;left:50%;transform:translateX(-50%);z-index:4;
width:min(86%,980px);text-align:center;pointer-events:none}
#truth .line1{font-size:21px;color:#fff0c5;letter-spacing:.04em}
#truth .line2{font-family:Arial,sans-serif;font-size:12px;color:#c6c5df;margin-top:7px;letter-spacing:.11em}
.badge{display:inline-block;border:1px solid rgba(255,211,115,.55);padding:5px 10px;border-radius:999px;
font-family:Arial,sans-serif;font-size:10px;letter-spacing:.15em;color:#ffe9ad;margin-top:10px;
background:rgba(20,12,48,.55)}
#hint{position:absolute;right:20px;bottom:18px;z-index:4;font:11px Arial,sans-serif;color:#777b9d}
canvas{display:block}
</style>
</head>
<body>
<div id="stage">
  <div id="hud">
    <div class="kicker">BREATH G • LIVING CALENDAR</div>
    <div class="title" id="dateLabel"></div>
    <div class="meta" id="meta"></div>
    <div id="badge"></div>
  </div>
  <div id="truth">
    <div class="line1">Wholeness does not become more whole.</div>
    <div class="line2">THE CENTER REMAINS INFINITE • THE HORIZON OF RELATIONSHIP MOVES</div>
  </div>
  <div id="hint">drag to turn • scroll to enter</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.161.0/build/three.min.js"></script>
<script>
const CFG = __CONFIG__;
const stage = document.getElementById('stage');
document.getElementById('dateLabel').textContent = CFG.dateLabel;
document.getElementById('meta').textContent =
  `FIELD ${CFG.yearRoot}  •  OCTAVE ${CFG.monthRoot}  •  PULSE ${CFG.dayRoot}  •  PHASE ${CFG.dateRoot}  •  PAIR ${CFG.pairLabel}`;
let badges=[];
if(CFG.gate) badges.push("1-GATE OPEN");
if(CFG.canonPair) badges.push("CANON PAIR");
document.getElementById('badge').innerHTML = badges.map(x=>`<span class="badge">${x}</span>`).join(" ");

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x02030d, .035);
const camera = new THREE.PerspectiveCamera(42, stage.clientWidth/stage.clientHeight,.1,100);
camera.position.set(0,0,8.4);

const renderer = new THREE.WebGLRenderer({antialias:true,alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(stage.clientWidth,stage.clientHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
stage.appendChild(renderer.domElement);

const group = new THREE.Group();
scene.add(group);

function hex(c){ return new THREE.Color(c); }
const c1=hex(CFG.palette[0]), c2=hex(CFG.palette[1]), c3=hex(CFG.palette[2]);

const starGeo = new THREE.BufferGeometry();
const starN=2400, starPos=new Float32Array(starN*3);
for(let i=0;i<starN;i++){
  const r=14+Math.random()*28, t=Math.random()*Math.PI*2, u=Math.acos(2*Math.random()-1);
  starPos[i*3]=r*Math.sin(u)*Math.cos(t);
  starPos[i*3+1]=r*Math.cos(u);
  starPos[i*3+2]=r*Math.sin(u)*Math.sin(t);
}
starGeo.setAttribute('position',new THREE.BufferAttribute(starPos,3));
const stars=new THREE.Points(starGeo,new THREE.PointsMaterial({size:.028,color:0xb9c2ff,transparent:true,opacity:.7}));
scene.add(stars);

const center = new THREE.Mesh(
  new THREE.SphereGeometry(.12,32,32),
  new THREE.MeshBasicMaterial({color:c1})
);
group.add(center);
const centerHalo = new THREE.Sprite(new THREE.SpriteMaterial({
  map: makeGlowTexture(CFG.palette[0]), color:c1, transparent:true, blending:THREE.AdditiveBlending, depthWrite:false
}));
centerHalo.scale.set(2.4,2.4,1);
group.add(centerHalo);

for(let i=0;i<5;i++){
  const ring=new THREE.Mesh(
    new THREE.TorusGeometry(.48+i*.23,.007,8,160),
    new THREE.MeshBasicMaterial({color:i%2?c2:c1,transparent:true,opacity:.32,blending:THREE.AdditiveBlending})
  );
  ring.rotation.set(i*.42,i*.68,i*.22);
  group.add(ring);
}

const sphereMat = new THREE.MeshPhysicalMaterial({
  color:0x5c4a9f, transparent:true, opacity:.10, roughness:.2, metalness:.05,
  transmission:.45, thickness:.35, side:THREE.DoubleSide,
  emissive:c3, emissiveIntensity:.08
});
const shell = new THREE.Mesh(new THREE.SphereGeometry(2.45,96,64),sphereMat);
group.add(shell);

const wire = new THREE.Mesh(
  new THREE.SphereGeometry(2.47,32,20),
  new THREE.MeshBasicMaterial({color:c1,wireframe:true,transparent:true,opacity:.09,blending:THREE.AdditiveBlending})
);
group.add(wire);

const memN=Math.floor(1500*CFG.memoryDensity);
const memGeo=new THREE.BufferGeometry();
const memPos=new Float32Array(memN*3);
const memCol=new Float32Array(memN*3);
for(let i=0;i<memN;i++){
  const r=Math.pow(Math.random(),.58)*2.15;
  const th=Math.random()*Math.PI*2, ph=Math.acos(2*Math.random()-1);
  memPos[i*3]=r*Math.sin(ph)*Math.cos(th);
  memPos[i*3+1]=r*Math.cos(ph);
  memPos[i*3+2]=r*Math.sin(ph)*Math.sin(th);
  const mix=Math.random();
  const cc=(mix<.33?c1:(mix<.66?c2:c3)).clone().lerp(new THREE.Color(0xffffff),Math.random()*.18);
  memCol[i*3]=cc.r;memCol[i*3+1]=cc.g;memCol[i*3+2]=cc.b;
}
memGeo.setAttribute('position',new THREE.BufferAttribute(memPos,3));
memGeo.setAttribute('color',new THREE.BufferAttribute(memCol,3));
const memories=new THREE.Points(memGeo,new THREE.PointsMaterial({
  size:.045,vertexColors:true,transparent:true,opacity:.78,blending:THREE.AdditiveBlending,depthWrite:false
}));
group.add(memories);

const eyes=[];
const trails=[];
const golden=Math.PI*(3-Math.sqrt(5));
for(let i=0;i<CFG.povCount;i++){
  const y=1-(i/(CFG.povCount-1))*2;
  const rad=Math.sqrt(1-y*y);
  const a=golden*i;
  const dir=new THREE.Vector3(Math.cos(a)*rad,y,Math.sin(a)*rad);
  const pos=dir.clone().multiplyScalar(2.49);

  const eye = new THREE.Group();
  eye.position.copy(pos);
  eye.quaternion.setFromUnitVectors(new THREE.Vector3(0,0,1),dir);
  const rim=new THREE.Mesh(
    new THREE.TorusGeometry(.055,.014,8,30),
    new THREE.MeshBasicMaterial({color:(i%3===0?c1:(i%3===1?c2:c3)),transparent:true,opacity:.9})
  );
  rim.scale.y=.58;
  const pupil=new THREE.Mesh(
    new THREE.SphereGeometry(.025,12,12),
    new THREE.MeshBasicMaterial({color:0x05020b})
  );
  pupil.position.z=.008;
  eye.add(rim,pupil);
  group.add(eye);
  eyes.push({obj:eye,phase:Math.random()*Math.PI*2,dir});

  if(CFG.showRays && i%3===0){
    const outward=pos.clone().add(dir.clone().multiplyScalar(.35+Math.random()*.8));
    const inward=dir.clone().multiplyScalar(.08);
    const curve=new THREE.CatmullRomCurve3([
      outward,
      pos.clone().multiplyScalar(.92),
      pos.clone().multiplyScalar(.55).applyAxisAngle(new THREE.Vector3(0,1,0),(.2-Math.random()*.4)),
      inward
    ]);
    const tube=new THREE.Mesh(
      new THREE.TubeGeometry(curve,42,.006,5,false),
      new THREE.MeshBasicMaterial({color:(i%2?c2:c3),transparent:true,opacity:.22,
        blending:THREE.AdditiveBlending,depthWrite:false})
    );
    group.add(tube);
    trails.push({obj:tube,phase:Math.random()*8});
  }
}

for(let i=0;i<18;i++){
  const curve=new THREE.EllipseCurve(0,0,2.75+i*.014,2.75+i*.014,0,Math.PI*2,false,0);
  const pts=curve.getPoints(180).map(p=>new THREE.Vector3(p.x,p.y,0));
  const geo=new THREE.BufferGeometry().setFromPoints(pts);
  const line=new THREE.Line(geo,new THREE.LineBasicMaterial({
    color:i%2?c1:c2,transparent:true,opacity:.018+i*.0015,blending:THREE.AdditiveBlending
  }));
  line.rotation.set(Math.random()*Math.PI,Math.random()*Math.PI,Math.random()*Math.PI);
  group.add(line);
}

const light1=new THREE.PointLight(c1,3.2,18); light1.position.set(4,3,5);scene.add(light1);
const light2=new THREE.PointLight(c2,2.4,16); light2.position.set(-4,-2,3);scene.add(light2);
scene.add(new THREE.AmbientLight(0x332a66,.7));

function makeGlowTexture(color){
  const cv=document.createElement('canvas');cv.width=cv.height=256;
  const ctx=cv.getContext('2d');
  const g=ctx.createRadialGradient(128,128,0,128,128,128);
  g.addColorStop(0,'rgba(255,255,255,1)');
  g.addColorStop(.12,color);
  g.addColorStop(.45,'rgba(145,90,255,.22)');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,256,256);
  return new THREE.CanvasTexture(cv);
}

let dragging=false,lastX=0,lastY=0,targetRX=.08,targetRY=0;
renderer.domElement.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY});
window.addEventListener('pointerup',()=>dragging=false);
window.addEventListener('pointermove',e=>{
  if(!dragging)return;
  targetRY+=(e.clientX-lastX)*.006;
  targetRX+=(e.clientY-lastY)*.006;
  lastX=e.clientX;lastY=e.clientY;
});
renderer.domElement.addEventListener('wheel',e=>{
  e.preventDefault();
  camera.position.z=Math.max(4.2,Math.min(12,camera.position.z+e.deltaY*.004));
},{passive:false});

const clock=new THREE.Clock();
function animate(){
  requestAnimationFrame(animate);
  const t=clock.getElapsedTime();
  const breath=(Math.sin(t*CFG.speed)+1)/2;
  const expansion=1+breath*.035+(CFG.gate?.022:0);
  shell.scale.setScalar(expansion);
  wire.scale.setScalar(expansion*1.003);
  center.scale.setScalar(1+.35*Math.sin(t*CFG.speed*2));
  centerHalo.scale.setScalar(2.2+.5*breath);
  centerHalo.material.opacity=.5+.35*breath;
  memories.rotation.y=t*.025;
  memories.rotation.x=Math.sin(t*.09)*.08;
  memories.material.opacity=.45+.4*breath;

  eyes.forEach((e,i)=>{
    const blink=.35+.65*Math.pow(Math.sin(t*.75+e.phase)*.5+.5,2);
    e.obj.scale.set(1,blink,1);
    const pulse=1+.18*Math.sin(t*1.4+e.phase);
    e.obj.children[0].material.opacity=.48+.48*pulse/1.18;
  });
  trails.forEach(tr=>{
    tr.obj.material.opacity=.08+.25*(.5+.5*Math.sin(t*.9+tr.phase));
  });

  if(CFG.autoOrbit) targetRY+=.00135;
  group.rotation.y+=(targetRY-group.rotation.y)*.035;
  group.rotation.x+=(targetRX-group.rotation.x)*.035;
  stars.rotation.y=t*.0025;

  renderer.render(scene,camera);
}
animate();

window.addEventListener('resize',()=>{
  camera.aspect=stage.clientWidth/stage.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(stage.clientWidth,stage.clientHeight);
});
</script>
</body>
</html>
'''.replace("__CONFIG__", json.dumps(config))

components.html(html, height=800, scrolling=False)

with st.expander("What this prototype is expressing"):
    st.markdown('''
- **The center never travels.** Its pulse changes visibility, not essence.
- **The circumference breathes.** Expansion represents an enlarging horizon of possible relationship.
- **POV-eyes awaken asynchronously.** No perspective is duplicated or expendable.
- **Experience rays curve inward.** Life goes outward; memory and meaning return to the common interior.
- **The interior becomes richer without becoming closed.** More color never removes its capacity for further experience.
- **The Breathing Calendar modulates the display.** Date roots influence palette, rhythm, activation, and gate emphasis.
    ''')

st.caption("Prototype language: Year = field • Month = octave • Day = pulse • Root = phase • Gate = return to One")
