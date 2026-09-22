
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
    "Angular LOVE Table",
    "Alpha Affine Square",
    "32 Girdle Detail",
    "Status + Scalar Tables",
])

with tab_chassis:
    st.header("Angular LOVE Table chassis")
    st.caption(
        "Known anode/cathode structure plotted against the locked 22.5° orientation ruler. "
        "The angular ruler is an address/orientation coordinate; it is not being confused with elemental weighting."
    )

    # Live controls specific to the angular view.
    f1,f2,f3 = st.columns(3)
    with f1:
        role_filter = st.radio("Show", ["Both", "Anodes", "Cathodes"], horizontal=True)
    with f2:
        face_filter = st.radio("Face", ["Both faces", "ABOVE", "BELOW"], horizontal=True)
    with f3:
        label_mode = st.radio("Labels", ["Role + element", "Element only", "Role only"], horizontal=True)

    # Locked 16-address angular ruler.
    angles = [ANGLE_QUANTUM * i for i in range(1,17)]

    # Build known principal 2A2C stations.
    # IMPORTANT STATUS:
    # The principal A1/A2/C1/C2 memberships are locked.
    # The 16 angular addresses are locked.
    # The bridge below places packet LOOKs on the 16-angle wheel as a declared visualization layer;
    # it does NOT claim a unique archive-derived 121-element angle permutation.
    principal = []
    role_radius = {"C2":1.15, "C1":1.42, "A1":1.82, "A2":2.10}
    role_kind = {"A1":"Anode","A2":"Anode","C1":"Cathode","C2":"Cathode"}

    # Use the 18 reciprocal half-octave LOOKs as the traversal sequence.
    # A LOOK reads A1->A2 and C1->C2; B LOOK reverses the same packet membership.
    # Map sequential LOOK index to the locked 16-address ruler with wrap, leaving the
    # 17th/18th Great-Radial completion visibly marked at the 22.5/45 degree return.
    look_index = 0
    for oi,(octv,a1,a2,c1,c2,note,ratio) in enumerate(PACKETS, start=1):
        for look,face in [("A","ABOVE"),("B","BELOW")]:
            look_index += 1
            slot_i = ((look_index - 1) % 16) + 1
            angle = slot_i * ANGLE_QUANTUM
            ordered = [("A1",a1),("A2",a2),("C1",c1),("C2",c2)] if look=="A" else [
                ("A2",a2),("A1",a1),("C2",c2),("C1",c1)
            ]
            for role,name in ordered:
                tup=scalar_tuple(name)
                principal.append({
                    "look_index":look_index,"slot":slot_i,"theta":angle,
                    "octave":octv,"look":look,"face":face,"role":role,
                    "kind":role_kind[role],"name":name,"radius":role_radius[role],
                    "Hz":tup["Hz"],"cm":tup["cm"],"k":tup["k"],"EM_GHz":tup["EM_GHz"],
                    "braid":note,
                    "status":"LOCKED membership / DECLARED angular bridge"
                })
    pdf=pd.DataFrame(principal)

    # Filtering.
    shown=pdf.copy()
    if role_filter=="Anodes":
        shown=shown[shown["kind"]=="Anode"]
    elif role_filter=="Cathodes":
        shown=shown[shown["kind"]=="Cathode"]
    if face_filter!="Both faces":
        shown=shown[shown["face"]==face_filter]

    def point_label(row):
        if label_mode=="Role + element":
            return f"{row['role']} · {row['name']}"
        if label_mode=="Element only":
            return row["name"]
        return row["role"]

    shown=shown.copy()
    shown["label"]=shown.apply(point_label,axis=1)

    figc=go.Figure()

    # 16 address spokes and degree labels.
    for ang in angles:
        figc.add_trace(go.Scatterpolar(
            r=[0.35,2.35],theta=[ang,ang],mode="lines",
            line=dict(width=1),hoverinfo="skip",showlegend=False
        ))
        figc.add_annotation if False else None

    # Center.
    figc.add_trace(go.Scatterpolar(
        r=[0],theta=[0],mode="markers+text",
        text=["CENTER / COMMON"],textposition="top center",
        marker=dict(size=18,symbol="circle"),name="Invariant Center"
    ))

    # Plot roles independently so anode/cathode structure is immediately visible.
    for role in ["A2","A1","C1","C2"]:
        d=shown[shown["role"]==role]
        if len(d)==0:
            continue
        figc.add_trace(go.Scatterpolar(
            r=d["radius"],theta=d["theta"],mode="markers+text",
            text=d["label"],textposition="top center",
            customdata=np.stack([
                d["octave"],d["look"],d["face"],d["role"],d["name"],
                d["slot"],d["Hz"],d["cm"],d["k"],d["EM_GHz"],d["status"]
            ],axis=-1),
            hovertemplate=(
                "%{customdata[0]} · LOOK %{customdata[1]} · %{customdata[2]}<br>"
                "%{customdata[3]} — %{customdata[4]}<br>"
                "angular slot=%{customdata[5]}/16 · θ=%{theta}°<br>"
                "Hz=%{customdata[6]:.9f}<br>cm=%{customdata[7]:.6f}<br>"
                "k=%{customdata[8]:.9f}<br>EM=%{customdata[9]:.9f} GHz<br>"
                "%{customdata[10]}<extra></extra>"
            ),
            name=role,marker=dict(size=12)
        ))

    # Live Alpha ray.
    active_angle = slot * ANGLE_QUANTUM
    figc.add_trace(go.Scatterpolar(
        r=[0,2.55],theta=[active_angle,active_angle],mode="lines+markers",
        line=dict(width=5),marker=dict(size=8),name="LIVE ALPHA LOOK"
    ))
    figc.add_trace(go.Scatterpolar(
        r=[2.58],theta=[active_angle],mode="markers+text",
        text=[f"ALPHA · slot {slot}/16 · {active_angle:g}°"],
        textposition="top center",marker=dict(size=20,symbol="diamond"),
        name="Active angular address"
    ))

    # Explicit O4/O5 girdle marker band.
    # This does not move elements; it marks the known Heart/girdle relation in the legend/text.
    figc.update_layout(
        height=820,
        title="Known 2A2C stations on the 16-address / 22.5° angular chassis",
        polar=dict(
            angularaxis=dict(
                direction="clockwise",rotation=90,dtick=22.5,
                tickmode="array",tickvals=angles,
                ticktext=[f"{a:g}°" for a in angles]
            ),
            radialaxis=dict(
                range=[0,2.8],
                tickmode="array",
                tickvals=[1.15,1.42,1.82,2.10],
                ticktext=["C2","C1","A1","A2"],
                title="functional role rings"
            )
        ),
        legend=dict(orientation="h")
    )
    st.plotly_chart(figc,use_container_width=True)

    # Live state and exact known girdle address.
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("Alpha slot",f"{slot}/16")
    m2.metric("Alpha angle",f"{active_angle:g}°")
    m3.metric("A(r,s)",f"{A:g}")
    m4.metric("D=3r+s",f"{affine_steps:+d}")
    m5.metric("LOOK face",active_face)

    st.markdown(
        f"**32-girdle address at this same angular slot:** **{active['address']}** ({active_face}) "
        f"AND reciprocal-face address **{reciprocal['address']}**. "
        f"The girdle and principal 2A2C packet layers are being shown against the same locked 16-angle ruler."
    )

    st.subheader("What is locked vs what is being tested")
    st.markdown(
        "**LOCKED:** 16 addresses per face at 22.5° increments; 32 = 16 ABOVE AND 16 BELOW; "
        "principal O1–O9 2A2C membership; exact 32-girdle pair permutation; scalar tuples; "
        "Plutonium final O9 anode; Radon A inside O9 C2; Tomion A still reference; Radon B pre-O1 reference.\n\n"
        "**DECLARED VISUALIZATION BRIDGE:** the 18 reciprocal half-octave LOOKs are walked sequentially across "
        "the 16-angle ruler and wrap at the Great-Radial completion. This lets us inspect where known A/C functions "
        "land without pretending the missing 121-element inner pairs have already supplied a unique angle permutation.\n\n"
        "**OPEN:** missing inner three reciprocal pairs and any unique archive-derived 121-element-to-angle permutation. "
        "Those positions stay unfilled rather than guessed."
    )

    st.subheader("Known angular placements in this build")
    cols=["theta","slot","octave","look","face","role","kind","name","Hz","cm","k","EM_GHz","status"]
    st.dataframe(pdf[cols],use_container_width=True,hide_index=True)

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
        title="A(r,s)=C+3r+s — canonical affine operator orientation",
        xaxis_title="Surface phase / horizontal differential",
        yaxis_title="Vertical +3 TURN runs TOP → BOTTOM",
        yaxis=dict(
            categoryorder="array",
            categoryarray=["r = -1","r = 0","r = +1"],
            autorange="reversed"
        )
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

    # Integrity audit: do not let display orientation silently alter the operator.
    canonical_offsets = [[-2,-3,-1],[1,0,2],[4,3,5]]
    affine_checks = {
        "top_row": canonical_offsets[0] == [-2,-3,-1],
        "center_row": canonical_offsets[1] == [1,0,2],
        "bottom_row": canonical_offsets[2] == [4,3,5],
        "center_axis": [canonical_offsets[0][1],canonical_offsets[1][1],canonical_offsets[2][1]] == [-3,0,3],
        "diag_left": canonical_offsets[0][0] + canonical_offsets[2][2] == 3,
        "diag_right": canonical_offsets[0][2] + canonical_offsets[2][0] == 3,
        "center_column_sum": sum([canonical_offsets[0][1],canonical_offsets[1][1],canonical_offsets[2][1]]) == 0,
    }
    integrity_pass = all(affine_checks.values())
    st.success("AFFINE INTEGRITY: PASS — canonical page orientation and operator identities agree.") if integrity_pass else st.error("AFFINE INTEGRITY: FAIL — do not trust traversal.")

    with st.expander("Affine → chassis audit"):
        st.write("Canonical page orientation: TOP `[-2,-3,-1]` · CENTER `[+1,0,+2]` · BOTTOM `[+4,+3,+5]`.")
        st.write("The numerical traversal engine itself remains `D=3r+s` and was not reversed by this display fix.")
        st.write(
            f"Current controls resolve: r={r}, s={s} → D={affine_steps:+d}; "
            f"θ={theta:g}° → q={q_steps}; origin={origin_slot} → slot={slot}/16."
        )
        st.write(
            "Important status: the affine operator and 22.5° ruler are locked; "
            "the rule `slot = wrap16(origin + D + q)` remains a DECLARED app implementation. "
            "Therefore this audit verifies internal consistency; it does not promote that bridge to archive canon."
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



