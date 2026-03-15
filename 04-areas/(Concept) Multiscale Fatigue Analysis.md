---
title: "Multiscale Fatigue Analysis"
date: 2026-03-13
tags: [research/fatigue, research/multiscale, engineering/composites, ai/surrogate, research/optimization]
aliases:
  - "멀티스케일 피로 해석"
  - "다중스케일 피로 분석"
description: "복합재료의 미시-거시 스케일을 연결하여 피로 수명을 예측하는 해석 방법론. AI를 활용한 계산 효율화가 핵심 트렌드."
---

# Multiscale Fatigue Analysis

## 개요

복합재료의 피로 거동을 **미시 스케일(섬유/매트릭스)부터 거시 스케일(구조물)**까지 연결하여 해석하는 방법론. 단일 스케일 해석으로는 포착할 수 없는 손상 메커니즘(매트릭스 크랙, 섬유 파단, 층간 분리 등)을 통합적으로 예측한다.

## 핵심 개념

- **Micro scale**: 섬유/매트릭스 단위의 손상 발생 및 진전
- **Meso scale**: 플라이(ply) 단위의 손상 축적
- **Macro scale**: 구조물 수준의 강성 저하 및 잔류 수명
- **Scale bridging**: 각 스케일 간 정보 전달 (homogenization, localization)

## AI 적용

- 멀티스케일 해석의 계산 비용이 매우 높음 → AI surrogate model로 대체
- 미시 스케일 RVE 해석 결과를 학습하여 거시 스케일에서 실시간 예측
- Physics-Informed Neural Network (PINN) 등 물리 기반 AI 모델 활용 가능

## Deep Dive (2026-03-13)

### 1. Scale Bridging의 실제 난이도 — 복합재 편차의 근본 원인

복합재는 두 가지 재료(섬유+매트릭스)의 결합이기 때문에 편차 소스가 매우 많다:

| 편차 소스 | 원인 | 영향 |
|----------|------|------|
| **Geometry 편차** | 섬유 배열, 체적분율, 두께 변동 | 미시 스케일 응력 분포 변화 |
| **폴리머 결합 조건** | 경화 온도/시간, 수지 유동 패턴 | 매트릭스 물성 산포 |
| **Interface 제조 결함** | 보이드, 층간 미접착, 수지 부족 | 층간분리 기점, 피로 수명 저하 |

이 편차들 때문에 현재 Building Block Approach(DNV-ST-0376 등)에서는 각 스케일 전환마다 **안전계수·보정계수를 실험으로 채워야** 한다. 편차를 전부 물리적으로 모델링하면 너무 복잡하고, 실험으로 채우면 시험이 과도하게 많아지는 딜레마.

### 2. AI 보정 모델 — 두 가지 접근법

| 접근 | 방식 | 장점 | 리스크 |
|------|------|------|--------|
| **A. 편차 자체를 학습** | 제조 파라미터 → 물성 산포 AI 예측 | 실험 횟수 대폭 감소 | 학습 데이터의 제조 조건 범위에 종속 |
| **B. 스케일 간 보정계수 학습** | micro→meso→macro 전환 보정 패턴 학습 | 기존 데이터 활용, 가이드라인 호환 | 물리적 해석 가능성(interpretability) 부족 |

**박사후 연구 방향은 B**:
- PI 연구실이 최적설계 전문 → 보정계수를 "고정값"이 아닌 **설계 변수**로 취급 가능
- AI surrogate로 스케일 전환 비용을 낮추면 → **멀티스케일 최적설계** 루프가 열림
- "해석 정확도를 높이는 AI" + "설계 루프에 넣는 최적화" = PI 연구실 강점과 시너지

기존 방식 vs AI 보정 모델:
```
[기존] Coupon 시험 → 안전계수(고정) → Element → 보정계수(고정) → 구조물 수명
[AI]   Coupon 데이터 → AI 스케일 전환 패턴 학습 → 조건별 최적 보정 → 구조물 수명
```

### 3. 데이터 확보 전략

| 우선순위 | 소스 | 내용 |
|---------|------|------|
| 1차 | 문헌 + 공개 DB | CMH-17, 논문 실험 데이터, NASA/FAA 공개 DB |
| 2차 | K-Carbon 시험 의뢰 | 연구비로 부족한 데이터 보충 (물성시험 분석) |

### Key Insight

> 복합재 멀티스케일 해석의 핵심 병목은 "스케일 간 보정"이다. 이를 실험으로 채우는 기존 방식 대신, AI가 기존 실험 데이터의 보정 패턴을 학습하면 시험 횟수를 줄이면서도 가이드라인과 호환 가능한 해석 체계를 구축할 수 있다. 최적설계 연구실의 전문성과 결합하면 "AI 보정 + 멀티스케일 최적설계"라는 차별화된 연구가 가능하다.

## 관련 노트

- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — 전체 논문 구조
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — 이 방법론을 PINN으로 구현 (CDM + DoE)
- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — 시계열 하중 이력 기반 수명 예측
- [[(Concept) Digital Twin Composites|Digital Twin]] — 이 해석 모델이 Digital Twin의 핵심 엔진
- [[(Concept) Structural Health Monitoring|SHM]] — 실측 데이터로 모델 보정
- [[(Concept) Virtual Certification|Virtual Certification]] — 해석 결과로 인증 대체
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트
