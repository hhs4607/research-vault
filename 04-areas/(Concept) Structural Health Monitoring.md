---
title: "Structural Health Monitoring (SHM)"
date: 2026-03-13
tags: [research/shm, engineering/composites, research/digital-twin, research/fatigue, research/rul, ai/pinn]
aliases:
  - "구조 건전성 모니터링"
  - "SHM"
  - "Health Monitoring"
description: "구조물에 센서를 부착하여 손상 및 열화를 실시간으로 감지하는 기술. Digital Twin의 데이터 입력원이며, AI 기반 손상 진단이 핵심 트렌드."
---

# Structural Health Monitoring (SHM)

## 개요

구조물에 **센서를 상시 부착**하여 손상 발생, 위치, 크기, 진전을 실시간으로 감지하는 기술. 기존 비파괴검사(NDI)가 주기적 점검이라면, SHM은 **연속적 모니터링**이다.

## 핵심 기술

| 기술 | 원리 | 특징 |
|------|------|------|
| **Acoustic Emission (AE)** | 손상 발생 시 방출되는 탄성파 감지 | 실시간 손상 감지 |
| **Guided Wave (Lamb Wave)** | 판 구조물 내 유도 초음파 전파 | 넓은 영역 스캔 가능 |
| **Fiber Optic Sensing (FBG)** | 광섬유 격자의 파장 변화 측정 | 분포형 변형률 측정 |
| **Vibration-based** | 고유진동수/모드 변화 감지 | 글로벌 손상 감지 |

## 복합재 SHM의 과제

- 복합재 손상 모드가 다양 (매트릭스 크랙, 층간분리, 섬유파단 등)
- 환경 요인(온도, 습도)에 의한 신호 변동
- 센서 자체의 내구성 및 구조물 통합 문제

## AI 적용

- 센서 신호에서 손상 특징(feature) 자동 추출
- 손상 유형 분류 (Classification)
- 손상 크기/위치 정량화 (Regression)
- 잔류 수명 예측과 연계

## SHM + Digital Twin Integration

SHM 데이터가 Digital Twin에 통합되면서 "주기적 점검" → "연속적 상태 기반 관리"로 패러다임이 전환되고 있다.

### 실측 데이터의 가치 — DTU Lillgrund Case

- Lillgrund 해상풍력 발전단지에서 strain gauge 측정 데이터를 피로 신뢰성 평가에 직접 사용한 결과, 모델 기반 대비 **연간 신뢰성 지수 ~33% 향상** (35년 운용 기준)
- **핵심 인사이트**: 실측 데이터를 사용하면 하중 불확실성 민감도가 거의 무시 가능 수준으로 감소. 모델만 사용하면 불확실성이 높아 과도하게 보수적인 수명 평가를 하게 됨
- 이는 SHM이 단순 손상 감지를 넘어 **수명 연장 판단의 핵심 근거**가 될 수 있음을 정량적으로 보여줌

### Digital Shadow vs Digital Twin

| 구분 | Digital Shadow | Digital Twin |
|------|---------------|-------------|
| **데이터 흐름** | 물리 → 가상 (단방향) | 물리 ↔ 가상 (양방향) |
| **피드백** | 없음 | 있음 (제어 반영) |
| **정확도** | 타워/블레이드 하중 재구성 오차 수 % 수준 | 더 높은 정확도 가능하나 구현 복잡 |
| **현실 성숙도** | 이미 실용 수준 도달 | 점진적 구현 중 |

- Kalman filter + 선형 공탄성 모델을 사용한 Digital Shadow만으로도 wake/shear 유동 조건에서 수 % 오차의 하중 재구성이 가능 (wtDigiTwin 프로젝트)

## AI-Driven SHM Trends (2024-2025)

최근 AI+SHM 연구 동향:

| AI 기법 | 적용 영역 | 특징 |
|--------|---------|------|
| **LSTM** | 시계열 응력 예측 | 노드 응력값 추세 예측 → 피로 손상 위치 조기 식별 |
| **CNN** | 손상 분류/탐지 | 비선형 구조 응답에서 미세 크랙/피로 패턴 인식 |
| **DNN** | 구조 응답 특징 추출 | 복잡한 데이터셋의 비선형 거동 해석 |
| **Physics-Informed NN** | 물리 제약 기반 예측 | 데이터 부족 시에도 물리적으로 타당한 예측 |

- AI+DT 모델이 전통적 주파수 영역 분석 대비 **손상 예측 정확도에서 유의미하게 우수**, 특히 소규모 크랙 발달과 연결부 피로 감지에서 강점
- 향후 트렌드: 멀티모달 NDT 시스템, 임베디드/무선 SHM, Industry 4.0 연계

## Deep Dive (2026-03-13)

### 1. SHM의 위치 — 1년 포닥 vs 장기 로드맵

Total Research Flow (GIST Kick Off 슬라이드 기준):
```
Material(Micro) ──→ Specimen(Macro) ──→ Scale-Up(Structure)
      │                    │                    │
  Material-AI         Structure-AI          SHM-AI
  PINN(Fatigue)      Digital Twin         Intelligent SHM
                     (AE/FBG)             → RUL Prediction
```

| 단계 | 내용 | 시기 |
|------|------|------|
| **Phase 1** | PINN 기반 피로 Degradation 모델 (Paper-3) | 1년 포닥 핵심 |
| **Phase 2** | DT 통합 — 해석 vs 센서 보정 | 포닥 후반~후속 |
| **Phase 3** | Intelligent SHM — 센서 실시간 역산 → RUL | 장기 비전 |

→ SHM은 **미래 확장 영역**이지만, PINN 피로 모델이 곧 Intelligent SHM의 핵심 엔진이 되므로 Phase 1의 성과가 Phase 3으로 직결됨.

### 2. Virtual Sensing — PINN이 곧 가상 SHM

물리 센서 없이도 PINN 모델이 "가상 센서" 역할:

| 구분 | Physical SHM | Virtual Sensing (PINN 기반) |
|------|-------------|--------------------------|
| **입력** | 실시간 센서 신호 | 제한된 측정 + 물리 모델 |
| **출력** | 측정 가능한 신호만 | 측정 불가능한 내부 상태까지 추론 |
| **복합재 적용** | 표면 strain, AE | 내부 층간분리, 매트릭스 크랙 밀도, 잔류 강도 |
| **비용** | 센서 설치/유지보수 | 계산 비용만 |

슬라이드의 "Intelligent SHM: 센서 데이터 실시간 역산 → 박리 길이/손상 상태 → RUL 산출"이 정확히 이 개념.

### 3. Transformer vs LSTM — 누적 손상에 왜 Transformer인가

> 상세 분석: [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]]

LSTM의 한계: **forgetting gate**가 장기 시퀀스에서 초기 정보를 소실시킴.

복합재 피로는 **누적 손상(cumulative damage)** — 수백만 사이클에 걸쳐 초기 손상이 최종 파괴에 기여. LSTM은 이 초기 이력을 "잊어버림."

| 모델 | 장기 의존성 | 누적 손상 적합성 | 물리 통합 |
|------|---------|-----------|--------|
| **LSTM** | 제한적 (forgetting gate) | 낮음 — 초기 손상 이력 소실 | 어려움 |
| **Transformer** | Self-attention으로 전체 이력 참조 가능 | 높음 — 임의 시점 참조 | Attention 가중치로 물리적 해석 가능 |
| **GRU-Attention** | Attention 추가로 개선 | 중간 | 부분적 |

**Transformer/GRU-Attention + PINN 하이브리드**:
- Transformer: 시계열 전체에서 손상 진전 패턴 학습 (어떤 시점의 하중이 최종 파괴에 기여하는지)
- PINN: 물리적 일관성 보장 (Degradation 지배방정식 내장)
- 결합 시: 물리적으로 타당하면서도 장기 누적 손상을 놓치지 않는 예측 모델

### Key Insight

> SHM은 1년 포닥의 직접 범위는 아니지만, PINN 피로 모델(Phase 1)이 곧 Virtual Sensing과 Intelligent SHM(Phase 3)의 핵심 엔진이 된다. Transformer+PINN 하이브리드는 복합재 누적 피로 손상의 장기 이력 추적에서 LSTM의 forgetting 문제를 해결하는 차별화된 접근이다. 이 전체 파이프라인은 Material(Micro) → Specimen(Macro) → Structure로 확장되며, 최종적으로 RUL 예측까지 연결된다.

## 관련 노트

- [[(Concept) Digital Twin Composites|Digital Twin]] — SHM 데이터가 Digital Twin에 입력
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — SHM 데이터로 해석 모델 보정
- [[(Concept) Virtual Certification|Virtual Certification]] — SHM 기반 condition-based 인증
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — PINN이 Virtual Sensing 핵심 엔진
- [[(Research) Paper-4 Transformer Fatigue Analysis|Paper-4: Transformer Fatigue]] — Transformer vs LSTM 상세 비교
- [[(Research) 포닥 논문 계획|논문 아이디어 노트]] — 4편 논문 계획
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트

## References

1. DTU Wind Energy, "Probabilistic lifetime extension assessment using mid-term data: Lillgrund wind farm case study", Wind Energy Science, [wes.copernicus.org](https://wes.copernicus.org/preprints/wes-2024-68/)
2. NREL wtDigiTwin, [github.com/NREL/wtDigiTwin](https://github.com/NREL/wtDigiTwin)
3. "Approach Towards the Development of Digital Twin for Structural Health Monitoring of Civil Infrastructure: A Comprehensive Review", Sensors 25(1), 2025, [mdpi.com](https://www.mdpi.com/1424-8220/25/1/59)
4. "Digital twin-based fatigue life assessment of orthotropic steel bridge decks using inspection robot and deep learning", Automation in Construction 172, 2025, [sciencedirect.com](https://www.sciencedirect.com/science/article/abs/pii/S0926580525000627)
5. Reliability Engineering & System Safety, Special Issue: "Structural Health Monitoring with Digital Twins", [sciencedirect.com](https://www.sciencedirect.com/journal/reliability-engineering-and-system-safety/special-issue/10GD37JX1LB)
