---
title: "Paper-3: PINN 기반 복합재 피로 Degradation 해석"
date: 2026-03-13
tags: [ai/pinn, research/fatigue, research/cdm, research/uq, research/doe, engineering/composites]
aliases:
  - "Paper-3"
  - "PINN Fatigue"
  - "PINN Degradation"
description: "PINN 기반 비선형 피로 degradation 해석 모델. CDM 접근법으로 강성 변화 기반 해석. Paper-2 (HyBC)의 선형 한계를 극복. DoE 기반 최소 시험 + PINN 내삽."
---

# Paper-3: PINN 기반 복합재 피로 Degradation 해석

## 연구 동기

Paper-2 (HyBC, Han et al. 2025)는 선형 피로 물성의 멀티스케일 역산법을 확립했으나, 다음을 반영하지 못함:
- 피로 중 비선형 강성 저하 (Stiffness Degradation)
- 계면 손상 진전 (매트릭스 크랙, 층간분리)
- 사이클 의존적 물성 변화

Paper-3은 **CDM(Continuum Damage Mechanics) 접근법**으로 강성 변화 기반 degradation을 PINN loss에 내장하여, 불확실성 정량화(UQ)가 내재된 비선형 피로 해석 모델을 구축한다.

> **주의**: 시계열 하중 이력 기반 Transformer 수명 예측은 [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4]]에서 별도 다룸.

## 물리 모델 — CDM 기반 강성 저하

### 접근법: CDM (강성 변화 기반)
- 복합재에서 개별 크랙 추적은 무의미 (복수 손상 모드가 동시 진행)
- **강성 저하(stiffness degradation)**를 손상 지표로 사용
- 측정 가능하고, 거시적으로 의미 있는 변수

### Degradation 법칙
- **Fiber**: E_f = E_f0 (1 - α_f · D_f^n_f) — 섬유 강성 저하
- **Matrix**: E_m = E_m0 (1 - α_m · D_m^n_m) — 매트릭스 강성 저하
- **Interface**: 방향은 **CZM → CDM 단순화 (Option A)**, 그러나 구체적 구현 미정
  - Damage 변수와 분리할지 합칠지 결정 필요
  - Interface 모델 조사 선행 필요
  - PI 협의 + 문헌 조사 후 확정

### 손상 진전 방정식 (CDM)
```
dD/dN = f(σ_max, R-ratio, D, material params)
```
- N에 따른 크랙 밀도가 아닌, **N에 따른 강성 변화**를 추적
- PINN이 이 진전 방정식을 loss에 내장

### PINN Loss 구조
```
L = L_data + L_BCD + L_BCN + L_Phys + L_gov
    (실험)   (경계조건D) (경계조건N) (물리법칙) (지배방정식)
```
- 실험 데이터(일부) + 해석 데이터(일부) 결합
- CDM 강성 저하 + (계면 손상 TBD)을 물리 loss에 내장

## 스케일 간 보정 전략

### 접근법 B: AI 학습 보정계수 (Deep Dive 1 도출)
- 고정 안전계수 → 조건별 최적 보정계수를 AI가 학습
- Transfer Learning: 스케일 간 보정 (micro ↔ meso ↔ macro)
- 최적설계 연구실 시너지: 보정계수 = 설계 변수 → 멀티스케일 최적설계 루프

## DoE 기반 실험 전략 (Deep Dive 4 도출)

### 핵심 개념
모든 적층 구성을 시험하는 대신, **DoE로 최소 시험 케이스를 선정**하고 PINN이 미시험 구성으로 내삽.

### 각도 의존성 + 적층 순서 보정
- **각도 보정**: 섬유 배향이 degradation에 미치는 영향 (0°, 45°, 90°)
- **적층 순서 보정**: 두께 방향 관찰 위치에 따른 degradation 차이 (표면 vs 중앙면, 대칭 vs 비대칭)
- DoE가 대표 구성을 선정 → PINN이 보정 매핑을 학습

### 시험 → 예측 파이프라인
```
DoE 선정 적층 구성 (최소 물리 시험)
    │
    ▼
Degradation 매핑 (S-N 곡선, 강성 감소 곡선)
    │
    ▼
PINN 학습 (CDM 물리 + 제한된 데이터)
    │
    ▼
미시험 구성 예측 (내삽 중심)
    │
    ▼
검증용 스팟 체크 시험 (K-Carbon, 선택적)
```

### 핵심 원칙
> PINN은 **예측기가 아닌 내삽/보정 도구**. DoE 검증 공간 내 내삽은 외삽보다 인증 관점에서 훨씬 유리하며, 각 물리 시험이 "시험 증폭기(test multiplier)" 역할. 목표 오차율: **<5%** (시편 단위).

### 데이터 전략

| 우선순위 | 소스 | 용도 |
|---------|------|------|
| 1차 | 문헌 + 공개 DB (CMH-17, NASA/FAA) | PINN 학습 데이터 |
| 2차 | K-Carbon 시험 의뢰 | 부족 데이터 보충 (연구비 활용) |

## UQ 프레임워크 (Deep Dive 2 & 4 도출)

### Bottom-up 불확실성 전파
```
HyBC (Paper-2): 라미네이트 시험 → 미시 물성 분포
    │
    ▼
Constituent 단위 확률 분포 (섬유 E_f, 매트릭스 E_m 산포)
    │
    ▼
Bayesian PINN: CDM Degradation 모델을 통해 전파
    │
    ▼
출력: 피로 수명 예측 + 신뢰 구간
```

### PINN 물리 잔차 = 불확실성 지표
- PDE 잔차가 높은 영역 = 모델 불확실성 높음
- Bayesian PINN posterior = 물리적으로 의미 있는 신뢰 구간
- Micro → Macro까지 추적 가능한 UQ chain

### 확률론적 검증 프레임워크 (Deep Dive 5 도출)
Lillgrund의 limit state equation **g = R - S**를 복합재 피로에 이식:
- **R** = 잔류 강도 (Bayesian PINN 예측, 분포)
- **S** = 적용 하중 스펙트럼 (분포)
- → 신뢰성 지수(reliability index) 직접 계산 가능

## PINN Virtual Sensing vs 물리 센서 (Deep Dive 5 도출)

DoE 내삽 + 물리 제약 하에서 PINN이 센서보다 우월할 수 있음:

| 조건 | 물리 센서 | PINN Virtual Sensing |
|------|---------|---------------------|
| **내삽 (DoE 범위 내)** | 점 측정 + 노이즈/드리프트 | 전체 field + 물리 제약 → **PINN 우위** |
| **물리 기반 외삽** | 측정 불가 (센서 없는 곳) | 물리 방정식이 구속 → **PINN 우위** |
| **미지의 파손 모드** | 실시간 감지 가능 | 모델에 없으면 예측 불가 → **센서 우위** |

## EASA CM-S-014 인증 매핑 (Deep Dive 4 도출)

| EASA 요구사항 | 섹션 | PINN + HyBC 대응 |
|-------------|------|-----------------|
| **Verification** | Sec. 4 | PINN loss 수렴 + PDE 잔차 최소화 + 해석해 벤치마크 |
| **Validation** | Sec. 5 | HyBC 역산 미시 물성의 쿠폰 레벨 검증 |
| **Calibration** | Sec. 5 | 교정 데이터(학습)와 검증 데이터(미사용 시험)의 명확한 분리 |
| **UQ** | Sec. 6 | Bayesian PINN posterior — constituent 단위부터의 bottom-up 확률 chain |
| **Extrapolation** | Sec. 7 | PINN 내장 물리가 외삽을 구속; DoE가 핵심 구성 공간 커버 |
| **Documentation** | Sec. 9 | 전체 파이프라인 추적 가능 |

### 외삽 문제 (핵심 미해결 과제)
- PINN 내장 물리가 순수 데이터 모델보다 외삽에 강건
- 규제 기관 승인에는 외삽 신뢰성의 **정량적 근거** 필요
- 전략: DoE로 경계 구성 커버 + PINN 물리 제약 + 외삽 영역에 Bayesian 불확실성 확대

## CerTest 프로젝트 비교 (Deep Dive 4 도출)

| 항목 | CerTest (EU, ~2025) | 본 연구 (2026~) |
|------|---------------------|----------------|
| 방법론 | 전통 FE + 통계 모델 + Bayesian | PINN (물리 내장 ML) |
| 스케일 | 멀티스케일 (쿠폰 → 구조) | 멀티스케일 (constituent → laminate) |
| 초점 | 정적 강도 / 손상 허용 | **피로 degradation** (차별화!) |

## Deep Dive (2026-03-14)

### 1. Choi et al. (2025) 대비 핵심 차별화 — 계산 효율의 질적 전환

단순 속도 차이가 아닌, Choi가 **할 수 없는 것**을 PINN이 가능하게 함:

| 능력 | Choi (FE+MCMC) | Paper-3 (PINN) |
|------|---------------|----------------|
| 1회 forward run | 분~시간 (FE) | **ms** (학습 후) |
| Full Monte Carlo (10,000회) | 수일~수주 | **수분** |
| 실시간 업데이트 | 불가 | 가능 → DT 엔진 |
| DoE 능동 학습 | 비현실적 | **가능** → 최소 시험 |
| 확률론적 민감도 분석 | 제한적 | 완전 가능 |

Choi의 MCMC가 FE 수천 회로 posterior를 얻는 반면, Bayesian PINN은 **학습 자체가 posterior 추정**. → Choi et al. 상세: [[(Paper) Choi 2025 Multiscale Bayesian Fatigue|Choi 2025 리뷰]]

### 2. Interface 고려 방향

- **방향**: CZM → CDM 단순화 (Option A)
- **미결정**: Damage 변수와 분리 vs 합침 — 추가 모델 조사 필요
- **조사 필요 사항**: CZM-CDM 변환 기존 연구, Choi et al.의 interface debonding 구현 방식
- **우선순위**: CDM bulk damage 먼저 구현 → interface는 후속 추가

### Key Insight

> Paper-3의 PINN은 Choi et al. (2025)의 FE+MCMC 대비 단순한 속도 향상이 아니라, 실시간 DT 업데이트와 DoE 능동 학습을 **가능하게 하는 질적 전환**. CDM 기반 강성 저하 모델은 개별 크랙 추적이 무의미한 복합재의 특성에 맞으며, interface는 CZM→CDM 방향으로 추후 모델 조사 후 구현 방식 확정. PINN의 본질은 "내삽/보정 도구"로서, DoE 검증 공간 내에서 <5% 오차의 완전한 보정 모델을 목표로 한다.

## 연구 공백 (문헌 조사 결과, 2026-03-13)

> **2025년 기준, "DoE 기반 적층 구성 선정 + PINN 내삽으로 미시험 구성의 피로 degradation 예측"을 통합 파이프라인으로 제시한 논문은 발표되지 않았음.** 이것이 Paper-3의 명확한 기여 포인트.

## 주요 관련 연구

### Category 1: PINN/ML 피로 모델 (적층 의존성 포함)

| 논문 | 방법 | 관련성 |
|------|------|--------|
| Rojas Sanchez & Waas (2024), Composites Part A | 멀티스케일 ML 피로 + NN surrogate | 가장 유사 — 차별화: PINN(물리 내장) vs 순수 NN |
| PIML for fatigue delamination (2024), Composites Part A | Physics-informed ML + fiber bridging | 제한 데이터 + 물리 제약 → 적층 간 일반화 |
| Fikry et al. (2025), JMRT | RF/LightGBM for matrix crack degradation | 다양한 적층 데이터셋 → ML 예측 (R²=0.88) |
| Arnold et al. (2023), NASA TM | MAC/GMC → MLP/RNN for S-N | 5400x 속도 향상 surrogate |

### Category 2: Bayesian 최적화 + 최소 시험

| 논문 | 방법 | 관련성 |
|------|------|--------|
| Chuaqui et al. (2021), Composites Part B | GP surrogate + Bayesian BO for stacking sequence | "어떤 적층을 시험할 것인가" BO 선례 |
| Probabilistic fatigue + BO (2025), Composite Structures | 사전 DB 없이 Bayesian 교정 | 최소 적층 데이터에서 BO 교정 |
| **Choi et al. (2025), Composite Structures** | 멀티스케일 확률 피로 + Bayesian 교정 | **가장 가까운 기존 연구** → [[(Paper) Choi 2025 Multiscale Bayesian Fatigue|별도 리뷰]] |

### Category 3: Transfer Learning + 제한 데이터

| 논문 | 방법 | 관련성 |
|------|------|--------|
| Zhong et al. (2025), Adv. Eng. Informatics | Neural ODE + sim→experiment TL | 시뮬 pretrain → 소량 실험 fine-tune |
| Liao et al. (2022), Polymers | Hashin + CLT 내장 NN + GA | Theory-guided ML for 적층 설계 |
| Boosting GFRTP fatigue (2025), Composites Part B | MC 증강 + 물리 제약 + LSTM TL | 미시험 조건 물리 제약 기반 증강 |

## 상태

- [ ] CDM degradation 지배방정식 확정
- [ ] Interface 고려 방법 결정 (PI 협의)
- [ ] PINN 아키텍처 설계 (CDM loss 임베딩)
- [ ] DoE 시험 매트릭스 설계 (적층 구성)
- [ ] 학습 데이터 확보 (문헌 + 공개 DB)
- [ ] 모델 학습 및 검증
- [ ] K-Carbon 추가 시험 (필요시)
- [ ] 논문 작성

## 관련 노트

- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — 전체 논문 구조
- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — 시계열 하중 이력 기반 수명 예측
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 핵심 방법론
- [[(Concept) Digital Twin Composites|Digital Twin]] — PINN이 DT 엔진
- [[(Concept) Virtual Certification|Virtual Certification]] — 인증 목표, EASA 프레임워크
- [[(Concept) Structural Health Monitoring|SHM]] — 미래 확장 (Virtual Sensing)
- [[(Paper) Lillgrund Probabilistic Lifetime Extension|Lillgrund 수명 연장]] — 확률론적 검증 프레임워크
- [[(Paper) Choi 2025 Multiscale Bayesian Fatigue|Choi et al. (2025) 리뷰]] — 가장 가까운 기존 연구 분석
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 과제 정보

## References

1. Han, H., Xia, Y., & Ha, S.K. (2025). Polymers, 17(2), 157. DOI: 10.3390/polym17020157
2. EASA, "CM-S-014", 2020
3. "Advancements in PINN for Laminated Composites", Mathematics 13(1), 2025
4. "Data-Efficient and Uncertainty-Aware RUL Prediction Using PINN", PHM Society
5. Rojas Sanchez & Waas (2024). Composites Part A. DOI: 10.1016/j.compositesa.2024.108539
6. Zhong et al. (2025). Adv. Eng. Informatics 69. DOI: 10.1016/j.aei.2025.104025
7. Liao et al. (2022). Polymers 14(15):3229. DOI: 10.3390/polym14153229
8. Chuaqui et al. (2021). Composites Part B 226. DOI: 10.1016/j.compositesb.2021.109347
9. Composite Structures (2025). DOI: 10.1016/j.compstruct.2025.119283
10. Choi et al. (2025). Composite Structures.
11. Composites Part A (2024) — PIML fatigue delamination
12. Fikry et al. (2025). JMRT.
13. Arnold et al. (2023). NASA TM-20230005410.
14. Int. J. Fatigue (2025) — limited testing data framework
