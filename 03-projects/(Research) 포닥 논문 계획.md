---
title: "Postdoc Paper Ideas — GIST Multiscale Fatigue + AI + Digital Twin"
date: 2026-03-13
tags: [research/fatigue, ai/pinn, ai/transformer, research/digital-twin, engineering/composites, research/multiscale]
aliases:
  - "논문 아이디어"
  - "Postdoc Paper Plan"
  - "GIST 포닥 논문 계획"
description: "GIST 박사후 국내연수 기간 중 계획된 4편의 논문 구조. Review + HyBC(출판) + PINN Degradation + Transformer RUL. Kick Off 미팅(2026.3.13) 자료 기반."
---

# Postdoc Paper Ideas

GIST Kick Off Meeting (2026.3.13) 슬라이드 및 딥다이브 논의를 기반으로 정리한 논문 계획.

## AI 활용 접근법 (슬라이드 05)

### 1. 계산 용이성 (Computational Efficiency)
1. Nonlinear, Degradation 해석에 대한 Surrogate Model 구축
2. 미리 학습된 RVE 기반 Nonlinear 해석 가능 (DMN)
3. 신호 수집 기반 신속한 SHM 예측 가능

### 2. 실험-해석 간극 보정 (Bridging the Gap)
1. 기존 복합재료 산업은 안전계수 기반 설계가 주류
2. 제조 편차, 모델의 복잡함으로 인해 정밀 해석이 어려움
3. AI 기반 최적화로 실험 데이터와의 편차 보정 가능 (PINN)

## 전체 연구 흐름

```
Material(Micro) ────→ Specimen(Macro) ────→ Scale-Up(Structure)
      │                      │                      │
  Material-AI           Structure-AI            SHM-AI
      │                      │                      │
  Paper-2: HyBC        Paper-3: PINN         Paper-4: Transformer
  (역산, 선형)          (Degradation/CDM)      (시계열 RUL)
      │                      │                      │
      └──────── Paper-1: Review (전체 로드맵) ────────┘
```

---

## Paper-1 (Review): Multiscale Fatigue Analysis — AI & Digital Twin Paradigm Shift

### 컨셉
복합재 피로 해석의 기술 계보 → AI 기반 DT로의 진화 로드맵 제시

### 3-Column 프레임워크

| Classical Multiscale (1960s~2020) | AI-Enhanced (2018~Present) | Digital Twin + SHM (Future) |
|----------------------------------|---------------------------|----------------------------|
| 거시적 현상 모델링 (1960s~80s) | **Speed-up**: Surrogate → ms 단위 해석 | **Virtual Certification**: AI 시뮬레이션으로 시험 대체 |
| 미시역학 & RVE (1990s~2010s) | **Bridging the Gap**: Transfer Learning으로 스케일 간 보정 | **Intelligent SHM**: 센서 역산 → 손상 상태 → RUL |
| 계면 손상 & Degradation (2010s~20s) | **손상 추적**: PINN + Transformer | **MRO 혁신**: Predictive Integrity 기반 선제 유지보수 |
| Computational Bottleneck | | |

### Review Scope
Classical Mechanics Limits → AI Speed & Gap Bridging → Digital Twin + Virtual Certification for SHM

### 상태
- [ ] 문헌 조사 진행
- [ ] 프레임워크 확정
- [ ] 초고 작성

---

## Paper-2 (Published): Back-calculation AI / Inverse Problem

### 컨셉
라미네이트 시험 데이터 → 미시 물성 역산 (HyBC)

### 핵심 내용
- **Forward**: Micro Properties → HyMicro → UD Lamina → HyCLT → Laminates (Excel)
- **Inverse (HyBC)**: Laminate test data → Back-calculate micro properties (Python)
  - min(Error_E, Error_S, Error_F)
- 실험 데이터와 일치하도록 미시 물성을 역산하는 피로 연산 알고리즘

### 한계 (→ Paper-3의 동기)
- 선형 해석법(MMFatigue)에 한정
- 비선형 거동 (Degradation, 물성 비선형) 반영 불가

### 출판 정보
- Han, H., Xia, Y., & Ha, S.K. (2025). *Characterization of fatigue properties of fiber-reinforced polymer composites based on a multiscale approach.* Polymers, 17(2), 157.
- DOI: https://doi.org/10.3390/polym17020157

### 상태: ✅ 출판 완료 (2025)

---

## Paper-3 (New): PINN 기반 Fatigue Degradation 해석

> **상세 노트**: [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Fatigue Degradation]] — CDM 모델, EASA 매핑, DoE 전략, UQ 프레임워크, 문헌 조사

### 컨셉
PINN 기반 비선형 피로 Degradation 해석 모델 — CDM 접근법으로 강성 변화 기반

### 핵심 요소
- **Physics**: CDM 기반 Fiber/Matrix degradation (강성 저하 추적, 크랙 개수 아님)
- **AI**: PINN — degradation 지배방정식을 loss에 내장
- **Scale Bridging**: 접근법 B — AI 학습 보정계수 (최적설계 연구실 시너지)
- **UQ**: Bayesian PINN — constituent 단위부터 bottom-up 확률 전파 (HyBC → PINN)
- **Data**: DoE 기반 최소 시험 + PINN 내삽 (목표 오차 <5%)
- **Certification**: EASA CM-S-014 credibility framework 준수
- **Interface**: 고려 방법 미정 (PI 협의 필요)

### 상태
- [ ] CDM degradation 지배방정식 확정
- [ ] Interface 고려 방법 결정
- [ ] PINN 아키텍처 설계
- [ ] DoE 시험 매트릭스 설계
- [ ] 학습 데이터 확보
- [ ] 모델 학습 및 검증
- [ ] 논문 작성

---

## Paper-4 (New): Transformer Algorithm in Fatigue Analysis

> **상세 노트**: [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — 아키텍처, LSTM 비교, 적용 시나리오

### 컨셉
Transformer Self-Attention으로 비선형 하중 이력(Load History)의 종속성을 포착하여 수명(RUL) 예측

### 핵심 요소
- **문제**: Miner's Rule은 하중 순서(Sequence Effect) 미반영, LSTM은 장기 이력 소실
- **해법**: Transformer Self-Attention이 전체 하중 이력 참조 → 순서 효과 학습
- **입력**: Raw time-series + 사이클 단위 압축 (순서 보존, 시퀀스 길이 축소)
- **출력**: 실시간 잔여 수명(RUL) 곡선
- **검증**: High→Low vs Low→High 비교 (Miner's Rule이 틀리는 경우를 올바르게 예측)
- **데이터**: 기존 S-N/Degradation 데이터 + **Paper-3 CDM 모델이 합성 데이터 공급**

### Paper-3과의 관계
- Paper-3 (PINN/CDM) → **Paper-4의 데이터 공급원** (합성 degradation 데이터 생성)
- Paper-4 (Transformer) → **Paper-3의 시계열 확장** (하중 순서 효과 반영)
- 미래 결합: Physics-Informed Transformer — 두 접근법의 장점 결합

### 상태
- [ ] Transformer 아키텍처 설계 (사이클 단위 압축 방식 확정)
- [ ] 학습 데이터 확보 (문헌 S-N + Paper-3 합성 데이터)
- [ ] HL vs LH Sequence Effect 검증
- [ ] Attention 가중치 물리적 해석 분석
- [ ] Paper-3과 결합 가능성 검토
- [ ] 논문 작성

---

## 논문 간 관계

```
Paper-2 (선형, 출판)
  │ "비선형 한계 → PINN으로 극복"
  ▼
Paper-3 (PINN Degradation, CDM 기반)     Paper-4 (Transformer RUL, 시계열 기반)
  │ "물리 모델 — 강성 저하"                 │ "데이터 모델 — 하중 순서 효과"
  │                                       │
  └──────────── 결합 가능 ─────────────────┘
                    │
                    ▼
            Paper-1 (Review, 전체 로드맵)
                    │
                    ▼
      Future: Digital Twin + Intelligent SHM + Virtual Certification
```

## 미래 확장 주제 (포닥 이후)

- **Physics-Informed Transformer**: Paper-3 + Paper-4 결합
- **Virtual Sensing**: 제한 센서 + PINN → 내부 손상 상태 추론 (= Intelligent SHM)
- **센서 배치 위상 최적화**: PI 전문 영역(위상 최적화) → PINN DT의 관측성 최대화하는 센서 배치
- **MRO 혁신**: Predictive Integrity 기반 선제적 유지보수

## 관련 노트

- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 과제 정보
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3 상세]] — PINN Degradation 전체 내용
- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4 상세]] — Transformer RUL 전체 내용
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 핵심 방법론
- [[(Concept) Digital Twin Composites|Digital Twin]] — DT 통합 비전
- [[(Concept) Structural Health Monitoring|SHM]] — 미래 확장
- [[(Concept) Virtual Certification|Virtual Certification]] — 인증 목표
