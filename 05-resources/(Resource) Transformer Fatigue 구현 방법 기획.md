---
title: "Transformer Fatigue Implementation Plan"
date: 2026-03-15
tags: [ai/transformer, research/fatigue, research/cdm, research/digital-twin, engineering/composites, research/rul]
aliases:
  - "Transformer 피로해석 기획"
  - "Transformer Fatigue Implementation"
description: "Transformer 기반 복합재 피로 해석 DT 코어 엔진의 상세 구현 기획. 모델 아키텍처, 데이터 토큰화, 물리 제약, 리스크 관리, 성공 게이트 등 A~H 전 영역 포괄."
source: "iCloud/10_Projects/03_Transformer_Fatigue/ (migrated 2026-03-15)"
---

# Transformer Fatigue Implementation Plan

Originally developed as a detailed implementation blueprint across 8 sections (A–H). Migrated from iCloud PARA vault on 2026-03-15.

---

## A. Purpose & Success Definition

### Project Goal

Real-time DT core engine: UN/ECE R134 sequence-based composite Type IV tank damage state (d_m, d_f) learned as block token sequences, with thermodynamically irreversible hard update + Transformer temporal kernel + (virtual sensor / EnKF / UQ) closed loop.

### Real-time Definition (Operational)

Not "1-second full 3D field" but **operational cycle unit state update**:
- Per block: state update (d_m, d_f), sensor QoI prediction, RUL distribution update
- Latency target: 0.1–1.0 s/block
- Speed-up vs FEM: 10³~10⁵× inference acceleration

### RUL as Distribution (Not Point Estimate)

- Accuracy: MAE/RMSE of RUL
- Calibration/Coverage: 90% prediction interval → empirical coverage ~85–95%
- Distribution quality: NLL or CRPS (optional but powerful)

### S1–S2–S3 Success Gates

**S1 — Surrogate PoC**
- QoI error: NRMSE below target
- Damage state error: d_m/d_f RMSE below target
- Physics violation rate ≈ 0%
- Speed-up: minimum 10³× over FEM
- Gate: 2 cases (H→L vs L→H) reproduce sequence effect; OOD (overload) shows no collapse

**S2 — Long-horizon Stability**
- Long rollout error does not explode over time
- Direct multi-step / Δ-increment learning improves stability quantitatively
- Inference within operational time budget
- Gate: 10×, 50× block rollout with error control, physics violation 0%, timing budget met

**S3 — SHM Integration**
- Virtual sensor masking: performance monotonically improves with sensor count (1/3/5/10…)
- Assimilation (pre/post): QoI error reduction, RUL distribution width reduction, coverage improvement
- Gate: Before/after update graphs for (1) QoI error vs time, (2) RUL PI width/coverage vs time

### Trustworthy AI — 6 Requirements

1. **Physics consistency**: irreversibility/upper bound via parametrized hard update
2. **Robustness/OOD**: no collapse on 4 OOD types; conservative fallback policy
3. **UQ**: RUL distribution + calibration (coverage)
4. **Traceability**: input token, model version, output state/RUL logging
5. **Explainability**: attention maps as reference only; permutation/ablation for quantitative attribution
6. **Safety fallback**: uncertainty-driven maintenance recommendation; assimilation divergence → safe mode

---

## B. Target & Application

### Scope Declaration (Paper 1)

- **Experimental validation at coupon level** (DIC-compatible)
- Type IV tank / COPV = application vision only, NOT experimental target
- Extensibility proven through token schema design (T, hold_time slots), geometry/layer tokens, virtual sensor/assimilation structure

### Coupon Target

- Variable-amplitude fatigue degradation of laminated composite coupons
- Recommended specimen: **OHT (Open Hole Tension)** — clear hotspot, DIC-friendly
- DIC role: block-end snapshot at reference load → 1:1 alignment with operational block update concept

### UN/ECE R134 Usage

- Not "R134 reproduced" but "R134-inspired DoE design emphasizing sequence effects"
- R134 justifies the need for block tokenization + sequence effect DoE

### 2-Track Strategy (Paper 1 Version)

- **Track A (Main)**: Coupon + DIC — full methodology verification
- **Track B (Optional)**: Same schema on more complex geometry (FEM-only) — extensibility demonstration in 1–2 figures

---

## C. Physics Scope / FEM

### Paper 1 Physics Scope

- Isothermal variable-amplitude fatigue (hold=0, T=constant)
- CDM-based: d_m (matrix), d_f (fiber) — 2 state variables
- Stiffness degradation:
  - E₂₂(d_m) = (1 - d_m) · E₂₂₀
  - G₁₂(d_m) = (1 - d_m) · G₁₂₀
  - E₁₁(d_f) = (1 - d_f) · E₁₁₀
- Extension slots for T, hold_time, tension/compression split (Paper 2)

### Effective Stress Coupling (Sequence Effect Driver)

σ̃ = σ / (1 - D)

- D = combination of d_m, d_f → past damage changes future damage rate
- This is the physics mechanism behind H→L vs L→H differences

### Cycle-jump / Block Stepping

Per block k:
1. Reference snapshot step: quasi-static at reference load → DIC-comparable QoI
2. Damage update step: UMAT updates Δd_m, Δd_f based on block token
3. Repeat for next block

### FEM Implementation

- **UMAT (Abaqus/Standard)** + Python external driver (recommended)
- State variables: d_m, d_f stored and updated per ply
- Block token passed via field variables or external driver

### Physics Risks

- R-C1: UMAT convergence failure near d→1 → viscous stabilization, damage clamp
- R-C2: CDM too simple → effective stress coupling + nonlinear damage rate
- R-C3: DIC vs FEM alignment → block snapshot at identical reference load, ROI comparison only
- R-C4: Excessive cycle-jump → ΔN scheduling, cross-validation with finer ΔN

---

## D. Data / Tokenization

### Core Principles

1. FEM data and future streaming use **same token schema**
2. Tokens are **block (ΔN) units** — cycle-by-cycle forbidden
3. DIC is **block-end snapshot verification**, not continuous measurement

### Minimum Token (Paper 1)

| Slot | Description | Paper 1 |
|------|-------------|---------|
| mode | {cycle, hold, snapshot} | cycle only |
| Smax, Smin | Stress amplitude | Variable |
| log₁₀(ΔN) | Block cycle count | Variable |
| T | Temperature | Constant (RT) |
| hold_time | Static hold duration | 0 |

### Extended Token (Future)

`mode, dt, Smax/Smin, Seq(equivalent fatigue), T, RH, hold_time`

- Seq: Rainflow-based equivalent fatigue stimulus summary
- RH: humidity (unused in Paper 1, slot retained)

### Sequence Effect DoE (Minimum 4 Types)

1. **H→L vs L→H pair** (mandatory, core validation)
2. **Overload spike** (OOD/robustness)
3. **Hold-time OOD** (FEM-only, extension slot verification)
4. **Temp/RH OOD** (optional, FEM-only)

### HDF5 Schema (Metadata-first)

```
/meta — schema_version, units, specimen_type, layup, material_props, fem_info, dic_info
/cases/<case_id>/
    inputs/
        load_tokens: [K, F]
        initial_state: [d_m0, d_f0]
        defect_token: (optional)
    targets/
        state_dm: [K] or [K, n_hotspots]
        state_df: [K] or [K, n_hotspots]
        qoi_hotspot_strain: [K, n_hotspots]
        qoi_dic_field: [K_snap, H, W, C] (optional)
    alignment/
        snapshot_ref_load, block_index_of_snapshots
/stats — mean/std, min/max, log scaling flags
```

### Virtual Sensor Masking Dataset

- sensor_pool_coords: [N_pool, 2]
- sensor_mask: [K_snap, N_pool] (0/1)
- Random masking (1/3/5/10 sensors) during training → sensor count performance curve

---

## E. Model / Training

### Main Model: Hotspot State-Space Transformer

Transformer serves as **temporal kernel** only — learns long-range dependency and sequence effects from block token sequences.

### Architecture

1. Embed(load_token) → E_load[t]
2. (Optional) Embed(state_{t-1}) → E_state[t]
3. E_in[t] = concat(E_load[t], E_state[t])
4. **Causal self-attention Transformer** (temporal axis)
5. Output heads: z_m[t], z_f[t], ε_pred[t]

Must have: causal mask + positional encoding

### Parametrized Hard Update (Thermodynamics-consistent)

```
d_{m,t} = d_{m,t-1} + (1 - d_{m,t-1}) · σ(z_{m,t})
d_{f,t} = d_{f,t-1} + (1 - d_{f,t-1}) · σ(z_{f,t})
```

- Irreversibility: Δd ≥ 0 guaranteed
- Upper bound: d ≤ 1 guaranteed
- Late-stage runaway prevention: increment shrinks as d→1

Optional weak physics penalty: L_order = ReLU(d_f - d_m)

### Δ-state / Δdamage Learning

- Predict increment (Δ), not absolute value (d)
- Reduces autoregressive drift in long rollouts
- Makes hard constraints easier to enforce

### Multi-step Rollout Loss

```
L = Σ_{h=1}^{H} w_h · (||d̂_{t+h} - d_{t+h}||² + α||ε̂_{t+h} - ε_{t+h}||²)
```

- Start with H=3~5, expand to H=10~20 after stabilization

### Scheduled Sampling

- Epoch 0~30%: teacher forcing 100%
- Epoch 30~70%: TF 100% → 20% linear decay
- Epoch 70%~end: TF 20% maintained

### Cross-attention (Layup × Load)

- Query = load tokens, Key/Value = layup tokens
- Each load step attends to plies → "which ply/orientation is most sensitive to this load?"
- Implementation order: prefix token first (fast PoC) → cross-attention upgrade (final paper)

### Spatio-Temporal ROM (Paper 1 Option / Paper 2 Main)

- POD (PCA) baseline: DIC field → POD coefficients a_t → Transformer predicts Δa_t → POD basis reconstruction
- Nonlinear AE (2D-CNN): Paper 2 upgrade for DIC ROI field prediction

### Baselines (Minimum 4)

1. XGBoost/MLP (no sequence effect)
2. LSTM/GRU (limited long-range dependency)
3. POD + LSTM (ROM + classical time-series)
4. POD + Transformer (same ROM, different temporal kernel)

---

## F. Evaluation / Verification / DT Operations

### 6-Axis Evaluation Framework

1. **Accuracy**: QoI/state prediction error (NRMSE, MAE)
2. **Long-horizon drift stability**: error vs horizon curve, divergence score
3. **Physics violation rate**: damage decrease / stiffness recovery / upper bound violations ≈ 0
4. **Efficiency**: speed-up vs accuracy trade-off (Pareto plot)
5. **OOD robustness**: 4-type benchmark performance
6. **DT operations**: UQ + Assimilation → sim-to-real gap reduction + coverage

### Long-horizon Evaluation Protocol

- Start from x₀, feed L_{1:K}, model uses own predictions as next input (real-world mode)
- Trajectory error vs horizon curve: NRMSE(h) for h=1..K
- Divergence score: average blocks until error exceeds threshold
- Failure time error: |t̂_f - t_f|

### OOD Evaluation (4 Types, All FEM-designed)

- Report accuracy + drift stability + physics violation rate + UQ response together

### UQ Options (Paper 1)

| Method | Pros | Cons |
|--------|------|------|
| Ensemble (5~10) | Strong calibration, clear distribution | N× inference cost |
| MC Dropout (20~50) | Lightweight | Variable quality |
| Heteroscedastic | Single forward pass | Risk of variance gaming |

### Assimilation: PC-EnKF (Projection-Constrained)

- Standard EnKF can violate irreversibility → projection after update:
  - d_m ← min(1, max(d_{m,prev}, d_m))
  - d_f ← min(1, max(d_{f,prev}, d_f))
- Alternative: EnKF in logit z space → d = σ(z) ensures bounds + monotone projection

### Coverage (UQ Verification)

- Nominal 50/80/95% intervals → empirical coverage measurement
- RUL coverage: predicted failure time distribution contains actual failure time?

---

## G. Novelty / Defense

### Primary Contributions (3)

1. **Thermodynamics-constrained Transformer**: parametrized hard update eliminates physics violations structurally
2. **Sequence Effect Attribution**: attention + permutation test + occlusion/ablation — quantitative evidence, not just heatmaps
3. **Virtual Sensor Masking → SHM Bridge**: full-field for training, sparse observation for operation

### Secondary Contributions (2)

4. **Mesh robustness**: coarse→fine generalization at QoI level
5. **Trustworthy surrogate**: physics≈0 + OOD + coverage + conservative fallback

### Attribution Protocol (3-Part)

1. Attention map visualization (candidate explanation)
2. Permutation test: shuffle block order → measure failure time / Δdamage change
3. Occlusion/Ablation: remove specific past block → quantify prediction change

### Key Defense Answers

- "Just use LSTM?" → LSTM fails H→L/L→H ordering, drifts on long horizons (quantitative comparison)
- "Attention ≠ causality" → Agreed; permutation/occlusion provide quantitative attribution evidence
- "Soft penalty is enough" → Penalty breaks on OOD; hard update guarantees violation≈0 structurally
- "DIC not practical in operation" → DIC = training rich observation; operation = sparse sensors via masking framework
- "Mesh changes = retraining?" → Mesh robustness tested (coarse→fine QoI generalization)

### Paper 1 Results Template (6 Figures)

1. Long-horizon drift curve
2. Physics violation rate (Train/Test/OOD, open-loop & post-assimilation)
3. OOD benchmark (4 types)
4. Speed-up vs accuracy Pareto
5. Virtual sensor masking (sensor count vs performance)
6. Coverage calibration curve (50/80/95%)

---

## H. Risk Management

### PM Structure Principles

1. Scope frozen around "MVP Paper 1"
2. Gate (Go/No-Go) controls phase transitions
3. Early warning → immediate mitigation pivot
4. Architecture risks sealed by structure (not tuning)
5. Experiment/analysis/training artifacts version-controlled

### Risk Register

**R1 — Data Generation Bottleneck (FEM Slow)**
- Early warning: wall-time >2× target, convergence failure >10–20%, weekly production <20 cases
- Mitigation: block stepping, output frequency reduction, hotspot QoI only, viscous stabilization, DoE reduction
- Plan B: Active sampling (uncertainty-driven FEM selection), Multi-fidelity (coarse/fine), limit D range to 0–0.8

**R2 — Autoregressive Drift**
- Early warning: exponential NRMSE growth, unstable failure time predictions
- Mitigation: Δ-state learning, multi-step rollout loss, scheduled sampling, direct multi-step alternative
- Plan B: Reduce MVP (1 hotspot, shorter blocks, minimal state variables)

**R3 — OOD Collapse / Non-physical Prediction**
- Early warning: physics violation >0, unrealistic failure times, overconfident UQ
- Mitigation: parametrized hard update, OOD 4-type protocol (never in training), OOD detection + conservative mode
- Plan B: Tone down claims to "violation≈0 + uncertainty increase + collapse prevention"

**R4 — O(N²) Memory / Scalability**
- Early warning: GPU OOM, seq_len scaling failure
- Mitigation: Transformer as temporal kernel only (short K), strong block aggregation, ROM latent for fields
- Plan B: Paper 1 closes with hotspot/QoI only, full-field is option

**R5 — Sim-to-Real Gap**
- Early warning: systematic bias between DIC and FEM QoI, poor reproducibility
- Mitigation: limited DIC sets for verification, virtual sensor masking, domain randomization, constrained assimilation
- Plan B: Paper 1 limits experimental validation to few QoI, focuses on methodology proof

**R6 — Explainability / Certification Barrier**
- Early warning: weak defense in lab meetings, black-box perception despite good results
- Mitigation: 3-part attribution (attention + permutation + occlusion), UQ + coverage, avoid overclaiming certification
- Plan B: Lower claims, strengthen quantitative evidence

### Phase-based Go/No-Go Gates

| Phase | Gate Condition |
|-------|---------------|
| **0: Scope/Schema Freeze** | Token schema, QoI, failure criterion fixed |
| **1: FEM Data Factory** | Convergence ≥80–90%, wall-time meets weekly target, 20–50 cases baseline works |
| **2: Baseline & MVP** | Hotspot accuracy at baseline level, Transformer improvement signal, K=20 rollout stable |
| **3: Physics + OOD** | Violation rate ≈ 0, OOD 2-type no total collapse, drift improved |
| **4: Virtual Sensor Masking** | 1/3/5/10 sensor performance curve, sparse observation still meaningful |
| **5: UQ + Assimilation** | Pre/post assimilation error reduction, coverage reasonable, gap reduced |

### Weekly KPI Dashboard (10 Items)

FEM: (1) avg wall-time/case, (2) convergence failure rate, (3) weekly case count, (4) storage/IO growth
Model: (5) long-horizon NRMSE slope, (6) physics violation rate, (7) OOD scores (2 types min)
DT/Trust: (8) UQ variance increase on OOD, (9) coverage (80%), (10) assimilation RMSE reduction

### Active Sampling Strategy

1. Initial 50–100 FEM cases → fast MVP training
2. Select cases where ensemble variance is high or OOD boundary
3. Far fewer FEM runs than random 500 sampling

### Multi-fidelity Fallback

- Low-fi: coarse mesh, simplified CDM, 2D/plane-stress, QoI only output
- High-fi: selected cases only, fine mesh, detailed damage
- Combined: weighted/corrected training

---

## Related Notes

- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — current GIST postdoc version
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — CDM model, data pipeline to Paper-4
- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — overall paper structure
- [[(Concept) Digital Twin Composites|Digital Twin]] — DT architecture context
- [[(Concept) Structural Health Monitoring|SHM]] — virtual sensing / sensor masking target
