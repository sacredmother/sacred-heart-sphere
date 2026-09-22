
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
# TOP STATUS
# -----------------------------
st.subheader("Living address")
m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("A(r,s)", f"{A:.0f}")
m2.metric("Affine D = 3r+s", f"{affine_steps:+d}")
m3.metric("q steps", f"{q_steps}")
m4.metric("Local slot", f"{slot}/16")
m5.metric("Active face", active_face)

st.markdown(
    f"### **{active['address']}**  — slot {slot}, θ-address {active['theta_deg']:g}°"
)
st.write(
    f"Reciprocal face at the same local address: **{reciprocal['address']}**. "
    f"Archived pair attached to this active address: **{active['mirror_address']}**."
)

# -----------------------------
# WALKING WHEEL
# -----------------------------
wheel = DF32.copy()
wheel["radius"] = np.log2(wheel["k"])
wheel["active"] = wheel["index"] == active["index"]
wheel["reciprocal_active"] = wheel["index"] == reciprocal["index"]

# row_for() returns a row from DF32 before the display-only radius column exists.
# Compute the active/reciprocal display radius directly from k.
active_radius = math.log2(float(active["k"]))
reciprocal_radius = math.log2(float(reciprocal["k"]))

fig = go.Figure()

for face in ["ABOVE","BELOW"]:
    d = wheel[wheel["face"] == face]
    fig.add_trace(go.Scatterpolar(
        r=d["radius"],
        theta=d["theta_deg"],
        mode="markers+text",
        text=d["slot"],
        textposition="top center",
        customdata=np.stack([d["address"],d["Hz"],d["cm"],d["k"],d["EM_GHz"]], axis=-1),
        hovertemplate=(
            "%{customdata[0]}<br>"
            "slot=%{text}<br>"
            "θ=%{theta}°<br>"
            "Hz=%{customdata[1]:.9f}<br>"
            "cm=%{customdata[2]:.6f}<br>"
            "k=%{customdata[3]:.9f}<br>"
            "EM=%{customdata[4]:.9f} GHz<extra>"+face+"</extra>"
        ),
        name=face,
        marker=dict(size=10 if face==active_face else 7, opacity=0.78),
    ))

# Active marker
fig.add_trace(go.Scatterpolar(
    r=[active_radius],
    theta=[active["theta_deg"]],
    mode="markers+text",
    text=[f"ACTIVE: {active['address']}"],
    textposition="top center",
    marker=dict(size=22, symbol="diamond"),
    name="Active Alpha address"
))
fig.add_trace(go.Scatterpolar(
    r=[reciprocal_radius],
    theta=[reciprocal["theta_deg"]],
    mode="markers+text",
    text=[f"RECIP: {reciprocal['address']}"],
    textposition="bottom center",
    marker=dict(size=18, symbol="circle-open"),
    name="Reciprocal face"
))

# Traversal path on active face
if show_path:
    path_slots = []
    start = origin_slot
    total_steps = affine_steps + q_steps
    direction = 1 if total_steps >= 0 else -1
    for k in range(abs(total_steps)+1):
        path_slots.append(wrap16(start + direction*k))
    pdpath = pd.DataFrame([row_for(active_face, sl) for sl in path_slots])
    fig.add_trace(go.Scatterpolar(
        r=np.log2(pdpath["k"]),
        theta=pdpath["theta_deg"],
        mode="lines+markers",
        name="Alpha traversal path",
        line=dict(width=3),
        marker=dict(size=6),
    ))

fig.update_layout(
    title="Alpha-driven 32-chassis walk",
    polar=dict(
        angularaxis=dict(direction="clockwise", rotation=90, dtick=22.5),
        radialaxis=dict(title="display radius = log₂(k)")
    ),
    height=650,
)
st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# ACTIVE SCALAR PACKET
# -----------------------------
st.subheader("Active scalar tuple")
a,b,c,d = st.columns(4)
a.metric("Hz", f"{active['Hz']:.9f}")
b.metric("cm", f"{active['cm']:.6f}")
c.metric("k", f"{active['k']:.9f}")
d.metric("EM GHz", f"{active['EM_GHz']:.9f}")

e,f,g,h = st.columns(4)
e.metric("Mirror Hz", f"{active['mirror_Hz']:.9f}")
f.metric("Mirror cm", f"{active['mirror_cm']:.6f}")
g.metric("Mirror k", f"{active['mirror_k']:.9f}")
h.metric("Mirror EM GHz", f"{active['mirror_EM_GHz']:.9f}")

st.markdown(
    f"**Exact local mirror law:** k′/k = {active['mirror_k']/active['k']:.6g}; "
    f"(Hz′/Hz)(cm′/cm) = {(active['mirror_Hz']/active['Hz'])*(active['mirror_cm']/active['cm']):.6g}."
)

# -----------------------------
# ALPHA AFFINE CHART
# -----------------------------
st.subheader("Affine operator state")
aff_rows=[]
for rr in range(r-2,r+3):
    for ss in [0,1,2]:
        val=alpha_affine(C,rr,ss)
        sl,ds,qs=alpha_to_local_slot(C,rr,ss,theta,origin_slot)
        rw=row_for(active_face,sl)
        aff_rows.append({
            "r":rr,"s":ss,"A":val,"D":val-C,"slot":sl,
            "address":rw["address"],"theta_address":rw["theta_deg"],
            "Hz":rw["Hz"],"cm":rw["cm"],"k":rw["k"],"EM_GHz":rw["EM_GHz"]
        })
aff=pd.DataFrame(aff_rows)

fig_aff=px.scatter(
    aff,x="s",y="r",text="slot",
    hover_name="address",
    hover_data=["A","D","theta_address","Hz","cm","k","EM_GHz"],
    title="Local Alpha affine neighborhood — each cell now resolves to a chassis address"
)
fig_aff.update_traces(marker_size=18,textposition="top center")
st.plotly_chart(fig_aff,use_container_width=True)

st.dataframe(aff,use_container_width=True,hide_index=True)

# -----------------------------
# 18-HALF-OCTAVE BRIDGE
# -----------------------------
st.subheader("Macro braid read")
sector_name, note_name = packet_from_slot(slot)
st.markdown(
    f"The active local slot lies in the app's four-sector macro display: **{sector_name} = {note_name}**."
)
st.caption(
    "Status: STRONG SYNTHESIS / visualization bridge. The archive locks the macro braid "
    "O1↔O8=Re, O2↔O7=Mi, O3↔O6=Fa, O4↔O5=Sol/Heart, but does not yet lock a unique "
    "one-to-one formula from every 16-slot local address to one macro pair. This app keeps that distinction visible."
)

# -----------------------------
# REFERENCE FUNCTIONS
# -----------------------------
st.subheader("Reference functions and O9 closure")
refs = pd.DataFrame([
    {
        "name":"Radon B",
        "membership":"outside O1",
        "role":"pre-O1 reflective / black-mirror cathodic reference",
        **scalar_tuple("Radon B")
    },
    {
        "name":"Tomion A",
        "membership":"outside periodic/RH spiral",
        "role":"still / invariant COMMON reference",
        **scalar_tuple("Tomion A")
    },
    {
        "name":"Radon A",
        "membership":"INSIDE O9 as C2",
        "role":"return cathodic / Mass-Hara closure",
        **scalar_tuple("Radon A")
    },
    {
        "name":"Plutonium",
        "membership":"INSIDE O9 as final anode",
        "role":"fullness-of-expression / terminal differentiated anode",
        **scalar_tuple("Plutonium")
    },
])
st.dataframe(refs,use_container_width=True,hide_index=True)

# -----------------------------
# STATUS / FORMALISM
# -----------------------------
with st.expander("Operator formalism and status"):
    st.markdown("""
**LOCKED internal operator**
- Alpha affine address: `A(r,s)=C+3r+s`
- Mirror: `J(C+D)=C-D`
- TURN quantum: `q=22.5°`, `q^16=I`
- 32 chassis: 16 compression/Tone-facing AND 16 rarefaction/Mass-harmonic-facing
- O9: Lutecium → Plutonium anodes; Xenon → Radon A cathodes
- Tomion A: still reference outside periodic spiral
- Radon B: pre-O1 reference outside O1
- Radon A: inside O9 as C2 closure

**Explicit app implementation**
- `slot = wrap16(origin + (3r+s) + θ/22.5°)`
- reciprocal face keeps the same local slot and changes LOOK face

This implementation is a **living traversal rule** built from the locked affine and TURN operators.
It is not being mislabeled as an already-retrieved archival theorem for the unique 16-address permutation.

**OPEN**
- full 121-element scalar completion
- exact archive-derived inner three reciprocal pairs across every half-octave
- unique source-derived formula connecting every 16-slot local address to one 18-half-octave macro packet
""")

st.divider()
st.caption(
    "Internal LOVE Table / Ω research interface. Whole first, operator second, number third, correspondence last."
)

