---
title: "Paper-4: Transformer Algorithm in Fatigue Analysis"
date: 2026-03-13
tags: [ai/transformer, research/fatigue, research/rul, engineering/composites, research/digital-twin]
aliases:
  - "Paper-4"
  - "Transformer Fatigue"
  - "Transformer RUL"
description: "Transformer의 Self-Attention 메커니즘을 활용한 비선형 하중 이력 기반 피로 수명(RUL) 예측. Miner's Rule과 RNN/LSTM의 한계를 극복. SHM 및 Digital Twin의 핵심 엔진."
---

# Paper-4: Transformer Algorithm in Fatigue Analysis

## 연구 동기

### 기존 접근법의 한계
- **Miner's Rule**: D = Σ(n_i/N_i) — 하중 순서(Sequence Effect) 미반영
- **Rainflow Counting**: 변동 하중을 등가 사이클로 변환하나, 순서 정보 소실
- **RNN/LSTM**: 장기 시계열에서 기울기 소실(Vanishing Gradient) 및 장기 의존성 학습 한계

### 복합재 피로의 특수성
- 피로 파괴는 하중의 **크기**뿐 아니라 **순서(Sequence Effect)**에 결정적 영향
- 초기 고응력 하중이 후기 저응력 피로 거동을 바꿈
- 수백만 사이클에 걸친 **누적 손상 이력** 전체가 중요

## 핵심 컨셉

### Self-Attention 기반 하중 이력 종속성 포착

```
Load History     →  Transformer        →  RUL Prediction
(Time-Series)       Self-Attention         잔여 수명 곡선
하중 시계열          NLP-based Encoder
```

- NLP 분야에서 검증된 **Transformer** 모델 도입
- **Self-Attention**으로 하중 순서에 따른 복잡한 피로 손상 패턴 학습
- 변동 하중 스펙트럼 하에서도 **실시간 잔여 수명(RUL) 예측 정확도 대폭 개선**
- 실시간 SHM 및 Digital Twin 구축의 핵심 엔진

### LSTM을 쓰지 않는 이유

| 모델 | 장기 의존성 | Sequence Effect 반영 | 물리적 해석성 |
|------|-----------|---------------------|-------------|
| **LSTM** | 제한적 (forgetting gate) | 초기 이력 소실 위험 | 낮음 |
| **Transformer** | 전체 (self-attention) | 임의 시점 간 관계 학습 | Attention 가중치 = 물리적 해석 가능 |
| **GRU-Attention** | Attention으로 개선 | 부분적 | 중간 |

- Forgetting gate가 초기 손상 이력을 소실 → 누적 피로 손상에 부적합
- Self-Attention은 전체 사이클 이력 참조 가능 → 어떤 하중이 최종 파괴에 기여하는지 학습

## Paper-3과의 관계

```
Paper-3: PINN Degradation          Paper-4: Transformer RUL
(CDM 기반 강성 저하 해석)            (시계열 하중 이력 기반 수명 예측)
         │                                    │
         │  물리 모델 (강성 변화)                │  데이터 모델 (하중 순서 패턴)
         │                                    │
         └──────────── 결합 가능 ────────────────┘
              PINN Degradation + Transformer RUL
              = 물리적으로 타당 + 장기 누적 손상 추적
```

- **Paper-3**: 물리(CDM) 중심 — 강성이 어떻게 저하되는가
- **Paper-4**: 데이터(시계열) 중심 — 하중 이력이 수명에 어떻게 영향하는가
- **미래 결합**: Physics-Informed Transformer — 두 접근법의 장점 결합

## 적용 시나리오

| 시나리오 | 입력 | 출력 |
|---------|------|------|
| **오프라인 수명 평가** | 설계 하중 스펙트럼 (전체) | 예상 피로 수명 |
| **실시간 RUL 예측** | SHM 센서 하중 이력 (실시간) | 잔여 수명 업데이트 |
| **하중 순서 최적화** | 다양한 하중 시나리오 | 수명 극대화 시퀀스 |

## Deep Dive (2026-03-14)

### 1. 입력 표현 — Raw Time-Series + 사이클 단위 압축

- **Raw time-series** 유지 → 순서 정보 완전 보존
- 단, 매 사이클이 아닌 **사이클 구간 압축** (cycle unit scaling)
  - 예: 10^6 사이클을 1000개 구간으로 압축
  - 각 구간: (σ_max, σ_min, ΔN, 누적 D 등)
- 순서 정보는 보존하면서 시퀀스 길이를 Transformer가 처리 가능한 수준으로 축소

### 2. 검증 전략 — High-Low vs Low-High 비교

핵심 가설: **Transformer는 하중 순서 효과를 포착하여 Miner's Rule이 틀리는 경우를 올바르게 예측**

| 하중 순서 | Miner 예측 | 실험 결과 | Transformer 기대 |
|----------|-----------|----------|-----------------|
| **High→Low** | D = 1.0 | D < 1 (조기 파괴) | Attention이 초기 고응력에 집중 → 조기 파괴 예측 |
| **Low→High** | D > 1.0 | D > 1 (오래 버팀) | Attention 분산 → 수명 연장 예측 |

- Attention 가중치 시각화 → **물리적 해석 가능**: "어떤 시점의 하중이 파괴에 결정적이었는가"
- HL/LH 비교는 논문의 **핵심 검증 시나리오**

### 3. 데이터 전략 — Paper-3 → Paper-4 파이프라인

```
기존 연구 데이터 (S-N, Degradation Curves)
    │
    ├── 실험 데이터 (문헌 + 공개 DB)
    │
    ├── 합성 데이터 (Paper-3 CDM/PINN 모델 기반)
    │   └── 물리 모델로 다양한 하중 순서 시나리오 생성
    │
    ▼
Transformer 학습
    │
    ▼
HL vs LH 검증 + RUL 예측
```

**Paper-3이 Paper-4의 데이터 공급원**: CDM 모델이 다양한 하중 순서에 대한 가상 degradation 데이터를 생성 → Transformer pretrain → 실험 데이터로 fine-tune

### Key Insight

> Paper-4의 Transformer는 Raw time-series를 사이클 단위 압축으로 입력받아 하중 순서 효과를 학습한다. HL vs LH 비교가 핵심 검증으로, Attention 가중치가 물리적 해석을 제공한다. 데이터 부족은 Paper-3의 CDM/PINN 모델이 합성 데이터를 생성하여 해결 — 이로써 Paper-3→Paper-4 파이프라인이 성립하며, 두 논문은 독립적이면서도 상호 보완적이다.

## 주요 참고 문헌

- Zhang, Z., Song, W., & Li, Q. (2022). "Dual-aspect self-attention based on transformer for remaining useful life prediction." *IEEE Transactions on Instrumentation and Measurement*, 71, Article 2505711. DOI: [10.1109/TIM.2022.3160561](https://doi.org/10.1109/TIM.2022.3160561)

## 상태

- [ ] Transformer 아키텍처 설계 (입력: 하중 시계열, 출력: RUL)
- [ ] 학습 데이터 확보 (변동 하중 피로 시험 데이터)
- [ ] Sequence Effect 검증 (하중 순서 변경 시 수명 변화)
- [ ] Paper-3 (PINN Degradation)과의 결합 가능성 검토
- [ ] 논문 작성

## 관련 노트

- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — 물리 기반 degradation (결합 대상 + 합성 데이터 공급)
- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — 전체 논문 구조
- [[(Concept) Structural Health Monitoring|SHM]] — 실시간 RUL 예측 → SHM 핵심
- [[(Concept) Digital Twin Composites|Digital Twin]] — DT 실시간 엔진
- [[(Concept) Virtual Certification|Virtual Certification]] — RUL 예측 → 인증 의사결정
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 피로 해석 방법론
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 과제 정보
- [[(Resource) Transformer Fatigue 구현 방법 기획|Transformer Fatigue 구현 기획]] — 상세 구현 기획 (아키텍처, 토큰화, 물리 제약, 리스크 관리, 성공 게이트)
