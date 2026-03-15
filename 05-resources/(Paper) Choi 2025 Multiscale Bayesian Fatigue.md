---
title: "Choi et al. (2025) — Multiscale Stochastic Fatigue Analysis with Bayesian Calibration"
date: 2026-03-13
tags: [research/fatigue, research/bayesian, engineering/composites, research/multiscale, research/uq, research/cdm]
aliases:
  - "Choi 2025"
  - "Bayesian Calibration Fatigue"
  - "SNU Multiscale Fatigue"
description: "서울대 Yun 연구실. CFRP 적층재의 멀티스케일 확률론적 피로 해석. Bayesian 교정(MCMC)으로 laminate 시험에서 constituent 피로 파라미터 분포를 역산. Paper-3의 가장 가까운 기존 연구."
source: "https://doi.org/10.1016/j.compstruct.2025.119122"
author: "Hoil Choi, Hyoung Jun Lim, Dongwon Ha, Jeong Hwan Kim, Gun Jin Yun"
---

# Choi et al. (2025) — Multiscale Stochastic Fatigue with Bayesian Calibration

## 논문 정보

| 항목 | 내용 |
|------|------|
| **저자** | Hoil Choi, Hyoung Jun Lim, Dongwon Ha, Jeong Hwan Kim, Gun Jin Yun |
| **소속** | Seoul National University |
| **저널** | Composite Structures, Vol. 363, Article 119122 |
| **출판일** | 2025 |
| **DOI** | [10.1016/j.compstruct.2025.119122](https://doi.org/10.1016/j.compstruct.2025.119122) |
| **SSRN Preprint** | [ssrn.com/abstract=4907189](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4907189) (무료 접근) |

## 연구 개요

FE 기반 멀티스케일 확률론적 피로 해석 프레임워크. Bayesian 교정으로 **거시 스케일(laminate) 피로 시험** 결과에서 **미시 스케일(fiber/matrix/interface) 피로 파라미터 분포**를 역산.

## 방법론

### 핵심 파이프라인
```
UD Laminate 피로 시험 (S-N, 잔류 강도, 잔류 모듈러스)
    │
    ▼
Bayesian Calibration (MCMC, Metropolis-Hastings)
    │  - Prior: constituent 피로 파라미터 사전분포
    │  - Forward model: micromechanics FE
    │  - Likelihood: 실험 데이터와의 일치도
    │
    ▼
Constituent-level 피로 파라미터 posterior 분포
    │  (fiber, matrix, interface 각각)
    │
    ▼
KL expansion + SSFEM으로 공간적 불확실성 통합
    │
    ▼
다양한 laminate 적층 구성의 확률적 피로 수명 예측
```

### 피로 모델
- **유형**: Micromechanics + CDM 혼합 접근
- **손상 변수**: fiber, matrix, interface 각각 독립적 손상 변수 + 손상 기울기
- **물성 저하**: 강성(stiffness) + 강도(strength) 저하를 FE에 사이클별 반영
- **물리 현상**:
  1. 구성성분의 물성 점진적 열화 (degradation)
  2. 매트릭스 내 국소 응력 집중 (local stress concentration)
  3. 점진적 계면 분리 (interface debonding)
- **하중 조건**: Tension-tension 피로

### Bayesian 교정 구체 방법
- **입력 (관측)**: UD laminate S-N 곡선, 잔류 강도/모듈러스
- **출력 (추정)**: fiber/matrix/interface 피로 파라미터의 posterior 분포
- **샘플링**: MCMC — Metropolis-Hastings 알고리즘
- **불확실성**: Karhunen-Loève (KL) 전개법으로 공간적 변동성 반영 (SSFEM)

### 검증
- 예측된 **피로 수명 분포** vs 실험 비교
- **파손 메커니즘 분포** 예측 및 검증
- 다양한 laminate 적층 구성에서 검증 (구체 layup 미확인 — full text 필요)

## Paper-3과의 비교 분석

| 항목 | Choi et al. (2025) | Paper-3 (본 연구) |
|------|-------------------|------------------|
| **역산 방법** | Bayesian MCMC 교정 | HyBC 역산 (확립됨, 출판) |
| **Forward 모델** | FE 기반 micromechanics | **PINN** (물리 내장 ML) |
| **속도** | FE → 느림 (MCMC에 수천 회 forward run 필요) | PINN surrogate → **빠름** (학습 후 ms 단위) |
| **확률론적 해석** | SSFEM + KL expansion | **Bayesian PINN posterior** |
| **손상 모델** | Micromechanics + CDM 혼합 | CDM (강성 변화 기반) |
| **Interface** | 점진적 debonding 고려 | 미정 (PI 협의) |
| **데이터 효율** | UD laminate 시험 필요 | DoE 기반 최소 시험 + 내삽 |
| **인증 매핑** | 없음 | EASA CM-S-014 프레임워크 |

### 차별화 포인트

1. **계산 효율**: Choi는 MCMC에 FE forward run 수천 회 필요. PINN은 학습 후 ms 단위 → 확률론적 해석이 실질적으로 가능
2. **HyBC 연결**: Paper-2로 이미 확립된 역산 파이프라인 위에 구축 (새 방법 개발 불필요)
3. **DoE 통합**: 어떤 적층을 시험할지 능동적으로 선정하는 전략 포함
4. **인증 프레임워크**: EASA 요구사항에 직접 매핑
5. **내삽/보정 도구**: 예측기가 아닌 보정 도구로 포지셔닝 → 높은 신뢰성

### 학습할 점

1. **Interface debonding** 고려 방법 — Choi는 이미 구현. Paper-3에서도 필요 (PI 협의 시 참고)
2. **KL expansion**: 공간적 불확실성을 체계적으로 표현하는 방법 — Bayesian PINN에도 적용 가능
3. **검증 메트릭**: S-N 곡선 + 잔류 강도 + 잔류 모듈러스 + 파손 메커니즘 분포 — Paper-3도 이 수준의 검증 필요

## 선행 논문 (같은 그룹)

- Kim, J.H., Ha, D., Choi, H., & Yun, G.J. (2024). "Multiscale fatigue life prediction model for CFRP laminates considering the mechanical degradation of its constituents and the local stress concentration of the matrix." Composite Structures.
  - [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0263822324006470)
  - 2025 논문의 결정론적(deterministic) 버전

## TODO

- [ ] SSRN에서 preprint PDF 다운로드하여 full text 분석
- [ ] 구체적 layup 구성 및 specimen 수 확인
- [ ] Interface debonding 모델 상세 확인 (Paper-3 참고용)
- [ ] 정량적 예측 정확도 (오차율) 확인

## 관련 노트

- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Degradation]] — 직접 비교 대상
- [[(Research) 포닥 논문 계획|포닥 논문 계획]] — 전체 논문 구조에서의 위치
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 공통 방법론
- [[(Concept) Virtual Certification|Virtual Certification]] — 인증 프레임워크
