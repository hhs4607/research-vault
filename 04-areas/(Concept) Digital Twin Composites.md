---
title: "Digital Twin for Composite Structures"
date: 2026-03-13
tags: [research/digital-twin, engineering/composites, ai/pinn, research/uq, research/fatigue, research/optimization]
aliases:
  - "디지털 트윈"
  - "복합재 디지털 트윈"
  - "Digital Twin"
description: "물리적 복합재 구조물의 실시간 디지털 복제본. 센서 데이터와 시뮬레이션 모델을 동기화하여 구조 상태를 가상으로 재현하고 수명을 예측한다."
---

# Digital Twin for Composite Structures

## 개요

물리적 구조물의 **실시간 디지털 복제본**. 센서 데이터(SHM)와 해석 모델(멀티스케일 피로 해석)을 동기화하여 구조물의 현재 상태를 가상으로 재현하고, 미래 거동을 예측한다.

## 핵심 구성 요소

| 구성 요소 | 역할 |
|----------|------|
| **Physical twin** | 실제 구조물 + 센서 |
| **Virtual twin** | 해석 모델 (FE, surrogate 등) |
| **Data link** | 센서 → 모델 데이터 동기화 |
| **AI engine** | 상태 진단 + 수명 예측 |

## 복합재 분야 적용

- 항공기 구조물의 실시간 건전성 평가
- 손상 허용 설계(Damage Tolerance)와 연계
- 비파괴검사(NDI) 주기 최적화
- 정비 일정 예측 (Predictive Maintenance)

## AI의 역할

- 물리 기반 해석의 계산 비용을 줄이는 surrogate model
- 센서 데이터의 노이즈 처리 및 패턴 인식
- 손상 상태 분류 및 잔류 수명 예측

## Quantitative Evidence (Field-Verified)

Digital Twin이 "개념"에서 "측정 가능한 성과"로 이동하고 있다는 최근 정량적 근거들:

### DTU Lillgrund Offshore Wind Farm Case

- **출처**: "Probabilistic lifetime extension assessment using mid-term data: Lillgrund wind farm case study" (Wind Energy Science, Copernicus)
- **핵심 결과**: 현장 strain gauge 측정 데이터를 사용한 피로 신뢰성 평가가, 모델 기반(Frandsen + generic aeroelastic) 평가 대비 **연간 피로 신뢰성 지수를 ~33% 향상**시킴 (35년 운용 기준)
- **의미**: 실측 데이터를 사용하면 하중 불확실성에 대한 민감도가 거의 무시할 수 있는 수준으로 감소. 반면 모델만 사용하면 불확실성이 높아 보수적 설계에 머묾
- **데이터**: DTU Figshare에 Lillgrund 시뮬레이션 피로 하중 데이터셋 공개

### wtDigiTwin — NREL Digital Twin (Kalman Filter 기반)

- **출처**: Branlard et al., "A digital twin based on OpenFAST linearizations for real-time load and fatigue estimation of land-based turbines" (NREL, 2020)
- **방법**: 선형 상태공간 모델 + 풍속 추정기 + Kalman filter → SCADA 데이터(타워 가속도, 발전기 토크, 피치, 회전속도)를 입력으로 하중 재구성
- **정확도**: 타워 fore-aft 굽힘모멘트 DEL 예측 정확도 **~5-10%** (시뮬레이션), 실측 대비 **10-15%** (풀스케일 프로토타입 검증, 부유식 해상풍력)
- **응용**: 실시간 피로 소진량 추정, 고장 감지, 수명 재평가

### Aviation/Airframe Digital Twin

- "A review and outlook of airframe digital twins for structural prognostics and health management in the aviation industry" (J. Manufacturing Systems, 2024)
- "Digital twin-based SHM by combining measurement and computational data: An aircraft wing example" (J. Manufacturing Systems, 2023)
- 항공기 복합재 구조물에 DT+SHM을 적용한 사례들이 축적 중

## Open-Source Tools & Datasets

| 도구/데이터 | 설명 | 링크 |
|-----------|------|------|
| **wtDigiTwin** | NREL 풍력 터빈 DT. SCADA + Kalman filter 기반 실시간 하중/피로 예측 | [github.com/NREL/wtDigiTwin](https://github.com/NREL/wtDigiTwin) |
| **OpenFAST** | NREL 다물리 풍력 터빈 시뮬레이션 (aero-hydro-servo-elastic). DT의 해석 백본 | [github.com/OpenFAST/openfast](https://github.com/OpenFAST/openfast) |
| **OpenWindSCADA** | 오픈 풍력 터빈 SCADA 데이터셋 큐레이션 + Jupyter 로더 | [github.com/sltzgs/OpenWindSCADA](https://github.com/sltzgs/OpenWindSCADA) |

## Research Implications

- 풍력 분야에서 DT+SHM 통합이 가장 앞서 있으며, 정량적 성과가 입증되기 시작
- 복합재 구조물(항공, 자동차 등)에는 동일 원리를 적용하되 **멀티스케일 손상 메커니즘** 반영이 추가 과제
- 오픈소스 도구와 데이터셋이 풍부해지면서 프로토타이핑/벤치마킹 가능
- **연구 기회**: 풍력 DT의 검증된 방법론 → 복합재 일반 구조물로 확장 (= 박사후 연구 방향과 일치)

## Deep Dive (2026-03-13)

### 1. Digital Twin 세대 진화 — 센서 수집에서 물리 모델 보정으로

DT의 기술 성숙도는 3세대로 구분할 수 있다:

| 세대 | 방식 | 특징 | 예시 |
|------|------|------|------|
| **1세대** | Data-driven | 센서 데이터 → 통계 모델 | 단순 이상 탐지 |
| **2세대** | Physics-corrected | 센서 + FE 모델 + Kalman filter | wtDigiTwin (NREL) |
| **3세대** | Optimization-integrated | 물리 모델 파라미터를 최적화로 보정 + 센서 동기화 | **연구 목표** |

3세대 DT의 핵심은 **모델 업데이트 문제 = 역 최적화 문제**라는 점:

```
minimize ||prediction(θ) - measurement||²
subject to: physics constraints (지배방정식, 경계조건)
```

→ 이것이 본질적으로 **최적화 문제**이며, PI 연구실(최적설계)의 전문 영역과 정확히 일치한다.

### 2. PINN 기반 DT — 물리 기반 스케일 최적화

PINN(Physics-Informed Neural Network)이 DT의 해석 엔진으로 적합한 이유:

| 장점 | 설명 |
|------|------|
| **물리 일관성** | 지배방정식(PDE)을 loss function에 포함 → 예측이 항상 물리적으로 타당 |
| **데이터 효율성** | 물리 제약이 regularizer 역할 → 적은 데이터로도 학습 가능 |
| **역문제 지원** | 파라미터 식별(parameter identification)을 자연스럽게 지원 = DT 보정의 핵심 |
| **멀티스케일 인코딩** | 각 스케일의 물리를 별도로 인코딩 가능 (micro: 구성방정식, meso: CLT, macro: 구조 응답) |

복합재 멀티스케일 DT에서 PINN의 역할:
```
[센서 데이터] → PINN (각 스케일 물리 내장) → [최적화로 파라미터 보정] → [수명 예측]
                    ↑                              ↑
              물리 제약 (PDE)              PI 연구실 전문 영역
```

**알려진 과제**: 복합재의 stiff PDE에서 PINN 학습 불안정성, multi-objective loss 밸런싱 등 — 그러나 adaptive weighting, curriculum learning 등 해결책이 활발히 연구 중이므로 오히려 좋은 연구 주제.

### 3. PINN 기반 Uncertainty Quantification (UQ)

순수 데이터 기반 surrogate와 PINN 기반 UQ의 근본적 차이:

| 구분 | 순수 데이터 기반 (GPR, MC Dropout) | PINN 기반 (Bayesian PINN) |
|------|-------------------------------|--------------------------|
| **불확실성 유형** | 통계적 (데이터 분포 기반) | 물리적 + 통계적 |
| **물리 위반 감지** | 불가능 | 물리 잔차(residual)로 감지 가능 |
| **신뢰 구간 근거** | "데이터가 부족한 영역" | "물리적으로 설명 안 되는 영역" |
| **인증 적합성** | 낮음 (규제 기관 설득 어려움) | 높음 (물리적 근거 제시 가능) |

핵심 인사이트:
- PINN의 **physics residual 자체가 불확실성 지표**로 작동 — residual이 높은 영역 = 모델이 불확실한 영역
- 이는 Virtual Certification에서 요구하는 **추적 가능한(traceable) 불확실성 경계**를 제공
- 규제 기관(FAA, EASA)에게 "이 예측의 불확실성은 이 물리적 가정에서 비롯됨"이라고 설명 가능

### 4. 연구 방향 통합 — 전체 그림

```
[Multiscale Fatigue]     [Digital Twin]        [Virtual Certification]
 AI 스케일 보정    →   PINN 기반 DT 엔진   →   물리 기반 UQ로 인증
 (Deep Dive 1)         (최적화 보정)            (불확실성 정량화)
       ↑                    ↑                        ↑
  PI 연구실: 최적설계 전문 — 전 과정이 최적화 문제
```

### Key Insight

> Digital Twin의 핵심 전환점은 "센서 데이터 수집"에서 "물리 모델의 최적화 기반 보정"으로의 진화다. PINN은 이 전환의 핵심 도구로, (1) 각 스케일의 물리를 내장하여 데이터 효율적 학습이 가능하고, (2) physics residual 기반의 물리적으로 의미 있는 불확실성 정량화를 제공한다. 이 전체 파이프라인이 본질적으로 최적화 문제이므로, 최적설계 연구실의 전문성과 완벽하게 시너지를 낸다.

## 관련 노트

- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — 전체 논문 구조
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — PINN이 DT의 해석 엔진
- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — 실시간 RUL 예측 엔진
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — Digital Twin의 핵심 해석 엔진
- [[(Concept) Structural Health Monitoring|SHM]] — Digital Twin에 실시간 데이터 공급
- [[(Concept) Virtual Certification|Virtual Certification]] — Digital Twin 기반 인증
- [[(Paper) Lillgrund Probabilistic Lifetime Extension|Lillgrund 수명 연장]] — DT 정량적 성과 근거
- [[(Resource) wtDigiTwin NREL|wtDigiTwin]] — DT 오픈소스 구현체
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트

## References

1. DTU Wind Energy, "Probabilistic lifetime extension assessment using mid-term data: Lillgrund wind farm case study", Wind Energy Science (Copernicus), [wes.copernicus.org](https://wes.copernicus.org/preprints/wes-2024-68/)
2. Branlard et al., "A digital twin based on OpenFAST linearizations for real-time load and fatigue estimation", NREL/TP-5000-76854, [docs.nrel.gov](https://docs.nrel.gov/docs/fy20osti/76854.pdf)
3. Branlard et al., "A digital twin solution for floating offshore wind turbines validated using a full-scale prototype", Wind Energy Science 9, 2024, [wes.copernicus.org](https://wes.copernicus.org/articles/9/1/2024/)
4. "A review and outlook of airframe digital twins for structural prognostics and health management", J. Manufacturing Systems, 2024, [sciencedirect.com](https://www.sciencedirect.com/science/article/pii/S0278612524002267)
5. Effenberger & Ludwig, "A collection and categorization of open-source wind and wind power datasets", Wind Energy, 2022
