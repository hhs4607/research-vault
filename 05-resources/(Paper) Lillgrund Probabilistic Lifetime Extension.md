---
title: "Added Value of Site Load Measurements in Probabilistic Lifetime Extension: A Lillgrund Case Study"
date: 2026-03-13
tags: [research/fatigue, research/wind-energy, research/digital-twin, research/reliability, engineering/composites, engineering/offshore]
aliases:
  - "Lillgrund 피로 신뢰성 연구"
  - "DTU Lillgrund fatigue study"
  - "Mozafari et al. 2026"
description: "Lillgrund 해상풍력 발전단지에서 실측 strain 데이터를 사용한 확률론적 수명 연장 평가. 모델 기반 대비 피로 신뢰성 지수 ~33% 향상을 정량적으로 입증한 논문."
source: "https://doi.org/10.5194/wes-11-621-2026"
author: "Shadan Mozafari, Jennifer Marie Rinker, Paul Veers, Katherine Dykes"
---

# Added Value of Site Load Measurements in Probabilistic Lifetime Extension: A Lillgrund Case Study

## 논문 정보

| 항목 | 내용 |
|------|------|
| **저자** | Shadan Mozafari (DTU / DNV), Jennifer M. Rinker (DTU), Paul Veers (NREL), Katherine Dykes (DTU) |
| **저널** | Wind Energy Science, Vol. 11, Issue 2, Article 621 |
| **출판일** | 2026년 2월 20일 |
| **DOI** | [10.5194/wes-11-621-2026](https://doi.org/10.5194/wes-11-621-2026) |
| **라이선스** | CC BY 4.0 |

## 연구 배경

- 풍력 터빈의 수명 연장(lifetime extension) 판단에는 현장 피로 신뢰성 평가가 핵심
- 기존 설계 단계에서는 Frandsen/IEC 난류 모델 + generic aeroelastic 모델에 의존
- 실제 현장 strain 측정 데이터를 사용하면 신뢰성 평가가 어떻게 달라지는가?

## 방법론

- **대상**: Lillgrund 해상풍력 발전단지 (스웨덴, compact layout)
- **접근**: 확률론적 프레임워크 (limit state equations 기반 신뢰성 분석)
- **비교 시나리오**:
  - (A) Frandsen 난류 모델 + generic aeroelastic 시뮬레이션 (전통적 설계 기반)
  - (B) 현장 strain gauge 측정 데이터 직접 사용
- **분석**: 단기 측정 데이터 → 장기 피로 예측으로 확률론적 외삽 (30년 return load 추정)

## 핵심 결과

- **실측 데이터 사용 시 연간 피로 신뢰성 지수 ~33% 향상** (35년 운용 기준, 모델 기반 대비)
- 실측 데이터를 사용하면 **하중 불확실성에 대한 민감도가 거의 무시 가능** 수준으로 감소
- 반면 Frandsen 모델 기반 평가에서는 하중 불확실성이 상대적으로 높음
- Compact layout 풍력 단지에서 Frandsen 모델의 적용 가능성 및 한계를 정량화

## 시사점

- **수명 연장 판단**: "보수적 설계" 기반 평가에서 "현장 특화(site-specific)" 평가로 전환 시 상당한 경제적 이점
- **SHM의 가치**: 실측 데이터가 단순 손상 감지를 넘어 **수명 연장 의사결정의 핵심 근거**가 됨
- **Digital Twin 연계**: 이 연구의 확률론적 프레임워크는 Digital Twin의 피로 수명 예측 모듈에 직접 적용 가능
- 4차례 revision을 거친 엄격한 peer review 통과

## 복합재 연구와의 연결

- 풍력 블레이드 자체가 GFRP/CFRP 복합재 구조 → 복합재 피로 연구에 직접 관련
- 확률론적 외삽 방법론은 복합재 구조물 일반으로 확장 가능
- AI surrogate model과 결합하면 계산 비용 절감 + 불확실성 정량화 동시 달성

## Deep Dive (2026-03-13)

### 1. PINN Virtual Sensing vs Physical Sensors — When PINN Wins

Lillgrund showed 33% reliability improvement from physical strain gauges. But PINN virtual sensing can potentially EXCEED sensor performance under specific conditions:

| Condition | Physical Sensor | PINN Virtual Sensing |
|-----------|----------------|---------------------|
| **Interpolation (within DoE)** | Point measurement + noise/drift | Full field + physics constraint → **PINN advantage** |
| **Physics-constrained extrapolation** | Cannot measure where no sensor exists | Physics equations constrain prediction → **PINN advantage** |
| **Unknown failure modes** | Real-time detection possible | Cannot predict outside model scope → **Sensor advantage** |

Key insight: If DoE covers the interpolation space and physics constraints are well-defined, PINN prediction confidence should be very high — potentially higher than noisy sensor data. For extrapolation to new configurations, physics constraints provide bounds that sensors physically cannot provide (sensors only measure where they are placed).

This inverts the traditional assumption that "real data always beats models." Within a well-designed DoE + physics framework, the model can be MORE informative than point measurements.

### 2. Probabilistic Framework Transfer to Paper-3

Lillgrund's limit state equation g = R - S is directly transferable to composite fatigue:
- **R** = residual strength (Bayesian PINN prediction with distribution)
- **S** = applied load spectrum (distribution)
- → Reliability index directly computable

This probabilistic framework should be adopted as Paper-3's output validation structure. Bayesian PINN provides distributions for both R and S, enabling direct reliability assessment comparable to Lillgrund's methodology.

### Key Insight

> Physical sensors have measurement uncertainty (noise, calibration, environmental drift). PINN has model uncertainty. Within DoE interpolation + physics constraints, model uncertainty can be LOWER than measurement uncertainty. PINN virtual sensing is not a sensor replacement but a complementary tool — excelling in interpolation and physics-constrained extrapolation, while sensors excel in detecting unknown-unknowns. Lillgrund's probabilistic limit state framework (g = R - S) maps directly to Paper-3's Bayesian PINN output validation.

## 관련 노트

- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Fatigue Degradation]] — Probabilistic framework adopted for output validation
- [[(Concept) Digital Twin Composites|Digital Twin]] — 이 논문의 프레임워크가 DT 피로 모듈에 적용 가능
- [[(Concept) Structural Health Monitoring|SHM]] — 실측 데이터의 가치를 정량적으로 입증
- [[(Concept) Virtual Certification|Virtual Certification]] — 확률론적 수명 평가 → 인증 대체 가능성
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트
