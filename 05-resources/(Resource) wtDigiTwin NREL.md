---
title: "wtDigiTwin — NREL Wind Turbine Digital Twin"
date: 2026-03-13
tags: [research/digital-twin, research/wind-energy, ai/kalman-filter, tool/open-source, research/fatigue]
aliases:
  - "wtDigiTwin"
  - "NREL Digital Twin"
  - "Wind Turbine Digital Twin"
description: "NREL에서 개발한 풍력 터빈 Digital Twin 오픈소스 소프트웨어. SCADA 데이터 + Kalman filter + OpenFAST 기반으로 실시간 하중/피로 추정."
source: "https://github.com/NREL/wtDigiTwin"
author: "Emmanuel Branlard (NREL)"
---

# wtDigiTwin — NREL Wind Turbine Digital Twin

## 개요

풍력 터빈의 하중, 운동, 환경 조건을 실시간으로 추정하는 Digital Twin 소프트웨어. SCADA 측정값과 물리 기반 모델을 결합하여, 직접 측정하지 않는 신호를 예측한다.

## 핵심 구조

```
SCADA 입력 → 선형 상태공간 모델 + Kalman Filter → 하중/피로 예측
(가속도, 토크,    (OpenFAST linearization     (풍속, 추력, 토크,
 피치, RPM)        또는 YAMS multibody)        타워 하중, 위치)
```

## 주요 기능

| 기능 | 설명 |
|------|------|
| **실시간 하중 추정** | 타워, 블레이드 등 핵심 부품의 하중 예측 |
| **피로 소진량 추정** | 핵심 부품의 실시간 fatigue consumption |
| **근본 원인 분석** | 상태 추정 기반 고장 감지 |
| **수명 재평가** | 서비스 수명 예측 업데이트 |
| **설계 개선** | 차세대 터빈 설계에 피드백 |

## 기술 스택

- **언어**: Python (51%), Fortran (49%)
- **핵심 라이브러리** (welib 하위 모듈):
  - `yams` — 다물체 동역학
  - `fast` — OpenFAST 모델 처리 및 선형화
  - `kalman` — Kalman filter 알고리즘
  - `fem` — 유한요소법
  - `ws_estimator` — Cp/Ct 테이블 기반 풍속 추정
- **라이선스**: MIT

## 설치

```bash
git clone --recurse-submodules https://github.com/NREL/wtDigiTwin
cd wtDigiTwin
python -m pip install -r requirements.txt
python -m pip install -e .
```

> `--recurse-submodules` 필수 (welib 의존성)

## 검증된 정확도

| 적용 | DEL 예측 오차 | 출처 |
|------|-------------|------|
| 육상 터빈 (시뮬레이션) | **~5-10%** | Branlard et al., 2020 |
| 부유식 해상 터빈 (풀스케일) | **~10-15%** | Branlard et al., 2023 (WES) |

## 관련 논문

1. Branlard et al., "Augmented Kalman filter with a reduced mechanical model to estimate tower loads on a land-based wind turbine", 2020
2. Branlard et al., "A digital twin based on OpenFAST linearizations for real-time load and fatigue estimation of land-based turbines", [NREL/TP-5000-76854](https://docs.nrel.gov/docs/fy20osti/76854.pdf)
3. Branlard et al., "A digital twin solution for floating offshore wind turbines validated using a full-scale prototype", [WES 9, 2024](https://wes.copernicus.org/articles/9/1/2024/)
4. Branlard & Geisler, "A flexible framework for multibody system models (YAMS)", 2022

## 복합재 연구와의 연결

- Kalman filter + 물리 모델 기반 상태 추정 방법론은 복합재 구조물에도 적용 가능
- OpenFAST의 선형화 접근을 복합재 FE 모델 선형화로 대체하면 유사한 DT 파이프라인 구축 가능
- 풍력 블레이드 자체가 GFRP/CFRP → 코드 내 피로 계산 모듈 직접 활용 가능

## Deep Dive (2026-03-13)

### 1. PINN Surrogate Speed → Probabilistic Fatigue Analysis

AI's core advantage: surrogate model replaces expensive FEM, enabling:
- Monte Carlo-style probabilistic analysis (thousands of realizations in seconds)
- Real-time degradation tracking (not post-processing)
- Kalman filter is optimal for linear/Gaussian systems, but composite fatigue is nonlinear + path-dependent → PINN has fundamental advantage for degrading systems

### 2. Fewer Sensors, Higher Accuracy

PINN-based DT can exceed simple sensor-based models in accuracy while reducing physical sensor count. Virtual sensing fills gaps between sparse sensor locations with physics-constrained predictions.

Architecture mapping from wtDigiTwin to composite DT:
- **Keep**: Sensor → State Estimator → Physics Model → Output (4-stage pipeline)
- **Replace**: Kalman → PINN, OpenFAST → Degradation governing equations, DEL → Residual strength/RUL

### 3. Accuracy Target: <5% Error

- wtDigiTwin benchmark: 5-10% DEL (onshore), 10-15% (floating offshore)
- Paper-3 target: **<5% at specimen level** — already achieved 5-10% in prior work
- Fatigue scatter is inherent; some error is unavoidable
- **Key framing: PINN as interpolation/correction tool, NOT extrapolation predictor**
  - Within DoE-covered space, PINN performs interpolation → high confidence
  - This framing is strategically important for certification: regulators accept validated interpolation far more readily than extrapolation claims

### Key Insight

> PINN's role in composite DT is best framed as a "complete correction/interpolation model" within DoE-validated space, not as a black-box predictor. This achieves surrogate speed (enabling probabilistic analysis), reduces physical sensor count through virtual sensing, and targets <5% error — defensible for certification because interpolation within validated bounds carries inherently lower risk than extrapolation. The wtDigiTwin 4-stage architecture (sensor → estimator → physics → output) transfers directly to composites with PINN replacing Kalman filter for nonlinear degradation tracking.

## 관련 노트

- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — Kalman→PINN 대체 아키텍처의 구현 대상
- [[(Concept) Digital Twin Composites|Digital Twin]] — 이 도구가 DT의 대표적 구현체
- [[(Concept) Structural Health Monitoring|SHM]] — SCADA 데이터 = SHM의 일종
- [[(Paper) Lillgrund Probabilistic Lifetime Extension|Lillgrund 수명 연장 연구]] — 관련 피로 신뢰성 연구
- [[(Resource) OpenWindSCADA Dataset|OpenWindSCADA]] — 벤치마킹용 SCADA 데이터셋
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트
