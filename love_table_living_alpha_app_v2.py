
import math
import cmath
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Living Alpha Affine Operator — LOVE Table Chassis v2",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Living Alpha Affine Operator — LOVE Table Chassis v2")
st.caption("Alpha now drives the address traversal. Change r, s, or θ and watch the active chassis address move.")

R_HZ_CM = 0.5414937759336099
C_LIGHT_GHZ_CM = 29.9792458
ANGLE_QUANTUM = 22.5

MASTER = {
    "Tomion B": (0.489375, 0.90375),
    "Radon B": (0.12234375, 0.2259375),
    "Alphanon / Einsteinium": (0.2446875, 0.451875),
    "Athenon / Lawrencium": (0.97875, 1.8075),
    "Betanon / Bohrium": (0.489375, 0.90375),
    "Quentin / Roentgenium": (1.9575, 3.615),
    "Gammanon / Moscovium": (0.97875, 1.8075),
    "Hydrogen": (3.915, 7.23),
    "Helium": (1.9575, 3.615),
    "Carbon": (7.83, 14.46),
    "Neon": (3.915, 7.23),
    "Silicon": (15.66, 28.92),
    "Argon": (7.83, 14.46),
    "Cobalt": (31.32, 57.84),
    "Krypton": (15.66, 28.92),
    "Rhodium": (62.64, 115.68),
    "Xenon": (31.32, 57.84),
    "Lutecium": (125.28, 231.36),
    "Radon A": (62.64, 115.68),
    "Tomion A": (250.56, 462.72),
    "Plutonium": (193.27, 356.847057),
}

PACKETS = [
    ("O1", "Tomion B", "Athenon / Lawrencium", "Radon B", "Alphanon / Einsteinium", "Re", 128),
    ("O2", "Athenon / Lawrencium", "Quentin / Roentgenium", "Alphanon / Einsteinium", "Betanon / Bohrium", "Mi", 32),
    ("O3", "Quentin / Roentgenium", "Hydrogen", "Betanon / Bohrium", "Gammanon / Moscovium", "Fa", 8),
    ("O4", "Hydrogen", "Carbon", "Gammanon / Moscovium", "Helium", "Sol / Heart", 2),
    ("O5", "Carbon", "Silicon", "Helium", "Neon", "Sol / Heart", 2),
    ("O6", "Silicon", "Cobalt", "Neon", "Argon", "Fa", 8),
    ("O7", "Cobalt", "Rhodium", "Argon", "Krypton", "Mi", 32),
    ("O8", "Rhodium", "Lutecium", "Krypton", "Xenon", "Re", 128),
    ("O9", "Lutecium", "Plutonium", "Xenon", "Radon A", "Great Radial / reset", None),
]

GIRDLE_PAIRS = [
    ("Livermorium", 7.4882, 28.30545, "Nitrogen", 14.7182, 113.2218),
    ("Tennessine", 7.7464, 28.30545, "Oxygen", 14.9764, 113.2218),
    ("Oganesson", 8.0046, 28.30545, "Fluorine", 15.2346, 113.2218),
    ("Gammanon / Moscovium", 1.8075, 1.769090625, "Helium", 3.615, 7.0763625),
    ("Helium", 3.615, 7.0763625, "Neon", 7.23, 28.30545),
    ("Lithium", 13.6853, 113.2218, "Sodium", 22.7228, 452.8872),
    ("Beryllium", 13.9435, 113.2218, "Magnesium", 22.981, 452.8872),
    ("Boron", 14.2017, 113.2218, "Aluminum", 23.2392, 452.8872),
]

def scalar_tuple(name):
    hz, cm = MASTER[name]
    k = hz * cm
    em = C_LIGHT_GHZ_CM / cm
    return dict(name=name, Hz=hz, cm=cm, k=k, EM_GHz=em)

def make_32_df():
    rows = []
    idx = 1
    passes = [
        ("ABOVE", "compression / Tone", [("O4", p, False) for p in GIRDLE_PAIRS] + [("O5", p, True) for p in GIRDLE_PAIRS]),
        ("BELOW", "rarefaction / Mass-harmonic", [("O5", p, True) for p in GIRDLE_PAIRS] + [("O4", p, False) for p in GIRDLE_PAIRS]),
    ]
    for face, face_role, seq in passes:
        slot = 1
        for side, p, reverse in seq:
            o4, cm4, k4, o5, cm5, k5 = p
            if reverse:
                name, cm, k, mirror, mcm, mk = o5, cm5, k5, o4, cm4, k4
            else:
                name, cm, k, mirror, mcm, mk = o4, cm4, k4, o5, cm5, k5
            hz = k / cm
            em = C_LIGHT_GHZ_CM / cm
            mhz = mk / mcm
            mem = C_LIGHT_GHZ_CM / mcm
            rows.append({
                "index": idx,
                "face": face,
                "face_role": face_role,
                "slot": slot,
                "theta_deg": slot * ANGLE_QUANTUM,
                "octave_side": side,
                "address": name,
                "mirror_address": mirror,
                "Hz": hz, "cm": cm, "k": k, "EM_GHz": em,
                "mirror_Hz": mhz, "mirror_cm": mcm, "mirror_k": mk, "mirror_EM_GHz": mem,
            })
            idx += 1
            slot += 1
    return pd.DataFrame(rows)

DF32 = make_32_df()

# -----------------------------
# ALPHA ADDRESS OPERATOR
# -----------------------------
def alpha_affine(C, r, s):
    return C + 3*r + s

def wrap16(n):
    # canonical local address labels are 1..16
    return ((int(n) - 1) % 16) + 1

def theta_step(theta_deg):
    return int(round(theta_deg / ANGLE_QUANTUM))

def alpha_to_local_slot(C, r, s, theta_deg, origin_slot=1):
    """
    Living address traversal.

    The affine displacement D = A-C = 3r+s is interpreted as an integer address displacement.
    θ contributes q-steps of 22.5°. The result wraps on the 16-address local face.

    This is an explicit implementation rule for the app, not a claim that archive canon
    already identified the unique discrete permutation formula.
    """
    D = alpha_affine(C, r, s) - C
    if abs(D - round(D)) > 1e-9:
        raise ValueError("For discrete address traversal, 3r+s must be an integer.")
    displacement = int(round(D))
    q_steps = theta_step(theta_deg)
    slot = wrap16(origin_slot + displacement + q_steps)
    return slot, displacement, q_steps

def mirror_slot(slot):
    """
    Reciprocal 16-face display partner: same local slot on the other face.
    The address-specific mirror element is taken from the 32-chassis table.
    """
    return slot

def row_for(face, slot):
    return DF32[(DF32["face"] == face) & (DF32["slot"] == slot)].iloc[0]

def packet_from_slot(slot):
    """
    Display bridge from the 16-slot local wheel to the 9-octave principal packet scaffold.
    Uses four 4-slot orientation sectors as an app visualization layer:
      slots 1-4  -> O1/O8 braid sector
      5-8        -> O2/O7
      9-12       -> O3/O6
      13-16      -> O4/O5
    This is labeled synthesis, not archive identity.
    """
    sector = (slot - 1) // 4
    return [
        ("O1 ↔ O8", "Re"),
        ("O2 ↔ O7", "Mi"),
        ("O3 ↔ O6", "Fa"),
        ("O4 ↔ O5", "Sol / Heart"),
    ][sector]

# -----------------------------
# CONTROLS
# -----------------------------
st.sidebar.header("Living Alpha driver")
C = st.sidebar.number_input("Invariant Center C", value=0.0, step=1.0)
r = st.sidebar.slider("Affine r", -8, 8, 0)
s = st.sidebar.selectbox("Affine surface s", [0,1,2], index=0, format_func=lambda v: {0:"R0 / s=0",1:"R1 / s=1",2:"R2 / s=2"}[v])
theta = st.sidebar.select_slider(
    "θ TURN",
    options=[0,22.5,45,67.5,90,112.5,135,157.5,180,202.5,225,247.5,270,292.5,315,337.5,360],
    value=0,
)
origin_slot = st.sidebar.slider("Declared local origin slot", 1, 16, 1)

face_mode = st.sidebar.radio(
    "LOOK / face",
    ["Compression / Tone", "Rarefaction / Mass-harmonic", "Auto reciprocal pair"],
    index=2,
)

show_path = st.sidebar.checkbox("Show traversal path from origin", value=True)

# -----------------------------
# COMPUTE LIVING ADDRESS
# -----------------------------
A = alpha_affine(C, r, s)
slot, affine_steps, q_steps = alpha_to_local_slot(C, r, s, theta, origin_slot)

if face_mode == "Compression / Tone":
    active_face = "ABOVE"
elif face_mode == "Rarefaction / Mass-harmonic":
    active_face = "BELOW"
else:
    # theta half-turn toggles presentation face in this implementation
    active_face = "ABOVE" if (q_steps // 8) % 2 == 0 else "BELOW"

active = row_for(active_face, slot)
other_face = "BELOW" if active_face == "ABOVE" else "ABOVE"
reciprocal = row_for(other_face, mirror_slot(slot))


# -----------------------------
# TABBED LIVING INTERFACE
# -----------------------------
tab_chassis, tab_alpha, tab_girdle, tab_status = st.tabs([
    "LOVE Table Chassis",
    "Alpha Affine Square",
    "32 Girdle Detail",
    "Status + Scalar Tables",
])

with tab_chassis:
    st.header("Living LOVE Table chassis")
    st.caption(
        "This is an unwrapped functional chassis, not a newly invented radial ruler. "
        "Horizontal position is the established O1→O9 packet order; vertical lanes are role lanes. "
        "The O4/O5 girdle seam is shown explicitly, while Alpha's current local address is carried beside it."
    )

    # Current live Alpha state
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("A(r,s)", f"{A:.0f}")
    m2.metric("D = 3r+s", f"{affine_steps:+d}")
    m3.metric("q steps", f"{q_steps}")
    m4.metric("Local slot", f"{slot}/16")
    m5.metric("LOOK face", active_face)

    # Build the exact principal 2A2C packet lanes.
    chassis_rows = []
    for i,(octv,a1,a2,c1,c2,note,ratio) in enumerate(PACKETS, start=1):
        for lane,role,name in [
            (3,"A2",a2),(2,"A1",a1),(-2,"C1",c1),(-3,"C2",c2)
        ]:
            tup = scalar_tuple(name)
            chassis_rows.append({
                "octave":octv,"x":i,"lane":lane,"role":role,"name":name,
                "Hz":tup["Hz"],"cm":tup["cm"],"k":tup["k"],"EM_GHz":tup["EM_GHz"],
                "braid":note
            })
    cdf = pd.DataFrame(chassis_rows)

    figc = go.Figure()

    # Four principal lanes.
    for role in ["A2","A1","C1","C2"]:
        d = cdf[cdf["role"]==role]
        figc.add_trace(go.Scatter(
            x=d["x"], y=d["lane"],
            mode="lines+markers+text",
            text=d["name"],
            textposition="top center" if role in ["A2","A1"] else "bottom center",
            customdata=np.stack([d["octave"],d["name"],d["Hz"],d["cm"],d["k"],d["EM_GHz"]],axis=-1),
            hovertemplate=(
                "%{customdata[0]} — "+role+"<br>"
                "%{customdata[1]}<br>"
                "Hz=%{customdata[2]:.9f}<br>"
                "cm=%{customdata[3]:.6f}<br>"
                "k=%{customdata[4]:.9f}<br>"
                "EM=%{customdata[5]:.9f} GHz<extra></extra>"
            ),
            name=role,
            marker=dict(size=11),
        ))

    # Invariant Center/COMMON lane.
    figc.add_hline(y=0, line_width=3)
    figc.add_annotation(x=5, y=0, text="Invariant Center / COMMON — does not move", showarrow=False, yshift=10)

    # O4/O5 girdle seam: explicit chassis hinge, not radial inference.
    figc.add_vrect(x0=3.5, x1=5.5, opacity=0.10, line_width=1)
    figc.add_annotation(
        x=4.5, y=4.25,
        text="O4 ↔ O5 HEART / 32-address GIRDLE SEAM<br>16 ABOVE AND 16 BELOW",
        showarrow=False
    )

    # Great Radial / O9 completion.
    figc.add_vrect(x0=8.65, x1=9.35, opacity=0.08, line_width=1)
    figc.add_annotation(
        x=9, y=4.25,
        text="O9 completion<br>Plutonium A2 / Radon A C2",
        showarrow=False
    )

    # Outside references: placed in a dedicated reference lane, not as periodic x-addresses.
    figc.add_annotation(
        x=0.55, y=-4.35,
        text="Radon B — outside O1<br>pre-O1 reflective reference",
        showarrow=True, ax=-15, ay=35
    )
    figc.add_annotation(
        x=9.45, y=4.85,
        text="Tomion A — outside periodic/RH spiral<br>still COMMON reference",
        showarrow=True, ax=15, ay=-30
    )

    # Girdle address badge: the live Alpha local address is shown at the seam.
    figc.add_annotation(
        x=4.5, y=0,
        text=(
            f"<b>LIVE ALPHA</b><br>{active['address']}<br>"
            f"{active_face} · slot {slot}/16 · θ-address {active['theta_deg']:g}°"
        ),
        showarrow=True, arrowhead=2, ax=0, ay=-80
    )

    # Principal reciprocal packet links.
    for i in range(1,10):
        a1 = cdf[(cdf.x==i)&(cdf.role=="A1")].iloc[0]
        a2 = cdf[(cdf.x==i)&(cdf.role=="A2")].iloc[0]
        c1 = cdf[(cdf.x==i)&(cdf.role=="C1")].iloc[0]
        c2 = cdf[(cdf.x==i)&(cdf.role=="C2")].iloc[0]
        figc.add_shape(type="line",x0=i,y0=2,x1=i,y1=3,line=dict(width=1))
        figc.add_shape(type="line",x0=i,y0=-2,x1=i,y1=-3,line=dict(width=1))

    figc.update_layout(
        height=760,
        title="Full principal 2A2C chassis with O4/O5 girdle seam",
        xaxis=dict(
            title="Established half-octave packet order",
            tickmode="array", tickvals=list(range(1,10)),
            ticktext=[f"O{i}" for i in range(1,10)],
            range=[0.25,9.75]
        ),
        yaxis=dict(
            title="Functional lane — schematic, not a scalar radius",
            tickmode="array",
            tickvals=[-3,-2,0,2,3],
            ticktext=["C2","C1","CENTER","A1","A2"],
            range=[-5.2,5.3]
        ),
        hovermode="closest",
        legend=dict(orientation="h")
    )
    st.plotly_chart(figc, use_container_width=True)

    st.markdown(
        f"**Current Alpha LOOK:** `{active['address']}` on the **{active_face}** face, "
        f"local slot **{slot}/16**. Its reciprocal-face address at the same local slot is "
        f"**{reciprocal['address']}**. The girdle is now shown *inside* the larger O1–O9 / 2A2C chassis rather than as the whole chassis."
    )

    st.info(
        "Rigor gate: the principal O1–O9 2A2C skeleton, O4/O5 girdle seam, 16+16 dual-face chassis, "
        "and reference placements are established. The missing inner three reciprocal pairs toward the literal 121-element completion "
        "remain OPEN and are not interpolated into this picture."
    )

with tab_alpha:
    st.header("Alpha Affine Square")
    st.caption(
        "The affine operator as its own live 3×3 square. This is magic-square-like affine geometry, "
        "not a conventional finite magic square requiring equal row/column/diagonal sums."
    )

    # Exact directional operator matrix around the invariant Center.
    offsets = np.array([[-2,-3,-1],[1,0,2],[4,3,5]], dtype=int)
    vals = offsets + C

    # Live point: highlight the residue class of D within this local 3×3 operator chart when present.
    Dint = int(round(A-C))
    labels = []
    for rr in range(3):
        row=[]
        for cc in range(3):
            off=int(offsets[rr,cc])
            v=vals[rr,cc]
            tag = "CENTER" if off==0 else f"C{off:+d}"
            if off==Dint:
                tag += "  ← LIVE D"
            row.append(f"{tag}<br>{v:g}")
        labels.append(row)

    figs = go.Figure(data=go.Heatmap(
        z=offsets,
        x=["R1 / +1","R0 / 0","R2 / +2"],
        y=["r = -1","r = 0","r = +1"],
        text=labels,
        texttemplate="%{text}",
        hovertemplate="offset=%{z:+d}<extra></extra>",
        showscale=False,
    ))

    # Center, crossed diagonal, and side-channel annotations.
    figs.add_annotation(x="R0 / 0",y="r = 0",text="<b>COMMON<br>C</b>",showarrow=False)
    figs.update_layout(
        height=600,
        title="A(r,s)=C+3r+s — local affine operator square",
        xaxis_title="Surface phase / horizontal differential",
        yaxis_title="Vertical ±3 TURN"
    )
    st.plotly_chart(figs,use_container_width=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Center C", f"{C:g}")
    c2.metric("A(r,s)", f"{A:g}")
    c3.metric("D=A−C", f"{A-C:+g}")
    c4.metric("θ", f"{theta:g}°")

    st.markdown(
        "**Exact square:**  \n"
        "`[-2  -3  -1]`  \n"
        "`[+1   0  +2]`  \n"
        "`[+4  +3  +5]`"
    )
    st.markdown(
        "Its crossed diagonals preserve **3 AND 3**: `−2 + 5 = 3` and `−1 + 4 = 3`. "
        "The center column preserves `−3 + 0 + 3 = 0`. The side-channel relation exposes the reciprocal **1/2 ↔ 2** read. "
        "The integers are the address/operator geometry; LOVE Table scalars are contents carried by addresses."
    )

    # Extended affine neighborhood, live with theta-resolved chassis slot.
    ext=[]
    for rr in range(r-3,r+4):
        for ss in [1,0,2]:
            aa=alpha_affine(C,rr,ss)
            sl,ds,qs=alpha_to_local_slot(C,rr,ss,theta,origin_slot)
            rw=row_for(active_face,sl)
            ext.append({
                "r":rr,"s":ss,"A":aa,"D":aa-C,"slot":sl,
                "chassis_address":rw["address"],"theta_address":rw["theta_deg"]
            })
    extdf=pd.DataFrame(ext)
    st.subheader("Extended affine lattice → live chassis resolution")
    st.dataframe(extdf,use_container_width=True,hide_index=True)

with tab_girdle:
    st.header("32-address dual-face girdle")
    st.caption("16 compression/Tone-facing addresses AND 16 rarefaction/Mass-harmonic addresses. Radius = log₂(k) is display-only.")

    wheel = DF32.copy()
    wheel["radius"] = np.log2(wheel["k"])
    active_radius = math.log2(float(active["k"]))
    reciprocal_radius = math.log2(float(reciprocal["k"]))

    fig = go.Figure()
    for face in ["ABOVE","BELOW"]:
        d = wheel[wheel["face"] == face]
        fig.add_trace(go.Scatterpolar(
            r=d["radius"], theta=d["theta_deg"], mode="markers+text",
            text=d["slot"], textposition="top center",
            customdata=np.stack([d["address"],d["Hz"],d["cm"],d["k"],d["EM_GHz"]], axis=-1),
            hovertemplate=(
                "%{customdata[0]}<br>slot=%{text}<br>θ=%{theta}°<br>"
                "Hz=%{customdata[1]:.9f}<br>cm=%{customdata[2]:.6f}<br>"
                "k=%{customdata[3]:.9f}<br>EM=%{customdata[4]:.9f} GHz<extra>"+face+"</extra>"
            ),
            name=face, marker=dict(size=10 if face==active_face else 7, opacity=0.78),
        ))

    fig.add_trace(go.Scatterpolar(
        r=[active_radius],theta=[active["theta_deg"]],mode="markers+text",
        text=[f"ACTIVE: {active['address']}"],textposition="top center",
        marker=dict(size=22,symbol="diamond"),name="Active Alpha address"
    ))
    fig.add_trace(go.Scatterpolar(
        r=[reciprocal_radius],theta=[reciprocal["theta_deg"]],mode="markers+text",
        text=[f"RECIP: {reciprocal['address']}"],textposition="bottom center",
        marker=dict(size=18,symbol="circle-open"),name="Reciprocal face"
    ))

    if show_path:
        path_slots=[]
        total_steps=affine_steps+q_steps
        direction=1 if total_steps>=0 else -1
        for kk in range(abs(total_steps)+1):
            path_slots.append(wrap16(origin_slot+direction*kk))
        pdpath=pd.DataFrame([row_for(active_face,sl) for sl in path_slots])
        fig.add_trace(go.Scatterpolar(
            r=np.log2(pdpath["k"]),theta=pdpath["theta_deg"],mode="lines+markers",
            name="Alpha traversal path",line=dict(width=3),marker=dict(size=6)
        ))

    fig.update_layout(
        height=700,title="Alpha-driven 32-address girdle",
        polar=dict(
            angularaxis=dict(direction="clockwise",rotation=90,dtick=22.5),
            radialaxis=dict(title="display radius = log₂(k)")
        )
    )
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Active scalar tuple")
    a,b,c,d = st.columns(4)
    a.metric("Hz",f"{active['Hz']:.9f}")
    b.metric("cm",f"{active['cm']:.6f}")
    c.metric("k",f"{active['k']:.9f}")
    d.metric("EM GHz",f"{active['EM_GHz']:.9f}")

    st.write(
        f"Archived mirror pair: **{active['address']} ↔ {active['mirror_address']}**. "
        f"k′/k = **{active['mirror_k']/active['k']:.6g}**."
    )

with tab_status:
    st.header("Status + scalar tables")

    refs = pd.DataFrame([
        {"name":"Radon B","membership":"outside O1","role":"pre-O1 reflective / black-mirror cathodic reference",**scalar_tuple("Radon B")},
        {"name":"Tomion A","membership":"outside periodic/RH spiral","role":"still / invariant COMMON reference",**scalar_tuple("Tomion A")},
        {"name":"Radon A","membership":"INSIDE O9 as C2","role":"return cathodic / Mass-Hara closure",**scalar_tuple("Radon A")},
        {"name":"Plutonium","membership":"INSIDE O9 as final anode","role":"fullness-of-expression / terminal differentiated anode",**scalar_tuple("Plutonium")},
    ])
    st.subheader("Reference and O9 roles")
    st.dataframe(refs,use_container_width=True,hide_index=True)

    st.subheader("32-address scalar chassis")
    st.dataframe(DF32,use_container_width=True,hide_index=True)

    st.subheader("Status discipline")
    st.markdown("""
**LOCKED / established in the current internal build**
- Alpha affine operator: `A(r,s)=C+3r+s`
- local directional square: `[-2,-3,-1; +1,0,+2; +4,+3,+5]`
- `q=22.5°`, with 16 local orientation addresses
- 32 girdle = 16 ABOVE AND 16 BELOW
- principal O1–O9 2A2C packet skeleton
- O4↔O5 Heart/girdle seam
- Plutonium = final O9 anode
- Radon A = INSIDE O9 as C2 return closure
- Tomion A = still reference outside periodic/RH spiral
- Radon B = pre-O1 reference outside O1

**DECLARED LIVING IMPLEMENTATION**
- `slot = wrap16(origin + (3r+s) + θ/22.5°)`
- This lets Alpha visibly traverse the chassis while remaining labeled as an implementation rule rather than an archival theorem.

**OPEN**
- literal 121-element completion
- missing inner three reciprocal pairs across every half-octave
- a unique archive-derived formula assigning every affine local address directly to every macro half-octave packet
""")

st.divider()
st.caption("Whole first, operator second, number third, correspondence last.")

