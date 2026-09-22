
# Living Alpha Affine Operator — LOVE Table Chassis v2

This version makes Alpha itself drive the chassis address traversal.

## Core live rule

The app implements:

A(r,s) = C + 3r + s

D = A - C = 3r + s

q = 22.5°

slot = wrap16(origin_slot + D + theta/22.5°)

Changing r, s, or theta therefore changes the active local chassis slot.

The active slot is immediately resolved to:

- named address
- reciprocal face address
- Hz
- cm
- k = Hz × cm
- EM GHz
- archived mirror address and mirror scalar tuple

## Status discipline

The affine and TURN operators are current internal canon.

The exact formula used to bind the affine displacement plus theta-step to a discrete 16-address slot
is an explicit app implementation so the operator can become "living." It is not mislabeled as an
already-retrieved archival theorem.

The app labels the macro 16-slot -> O1/O8, O2/O7, O3/O6, O4/O5 sector bridge as synthesis.

## Current canon corrections preserved

- Plutonium = final O9 anode
- Radon A = INSIDE O9 as C2 return / Mass-Hara closure
- Tomion A = still reference outside periodic/RH spiral
- Radon B = pre-O1 reflective reference outside O1

## Run

```bash
python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
streamlit run love_table_living_alpha_app_v2.py
```
