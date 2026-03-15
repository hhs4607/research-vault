---
title: "Virtual Certification for Composite Structures"
date: 2026-03-13
tags: [research/certification, engineering/composites, ai/pinn, research/uq, research/bayesian]
aliases:
  - "가상 인증"
  - "Virtual Allowables"
  - "Certification by Analysis"
  - "Virtual Testing"
description: "실물 시험 대신 시뮬레이션 기반으로 복합재 구조의 안전성을 인증하는 접근법. Building Block Approach의 시험 비용을 획기적으로 줄이는 것이 목표."
---

# Virtual Certification for Composite Structures

## 개요

복합재 구조 인증의 전통적 방식인 **Building Block Approach (BBA)**는 쿠폰 → 요소 → 서브컴포넌트 → 풀스케일까지 수천 건의 시험을 요구한다. Virtual Certification은 이 **시험의 일부 또는 전부를 시뮬레이션으로 대체**하여 비용과 시간을 절감하는 접근법이다.

## Building Block Approach vs Virtual Certification

| 단계 | 전통 BBA | Virtual Certification |
|------|---------|----------------------|
| Coupon | 물리 시험 수천 건 | 시험 + AI surrogate |
| Element | 물리 시험 수백 건 | 시뮬레이션 대체 가능 |
| Sub-component | 물리 시험 수십 건 | Digital Twin 활용 |
| Full-scale | 필수 시험 | 시험 축소 + 가상 보완 |

## 규제 동향 (상세)

### EASA CM-S-014 — M&S 기반 구조 인증 가이드라인

- 2020년 발행, CS-25 (대형 항공기) 구조 인증에 M&S 적용 지침
- **Credibility Framework** 핵심 요구사항:
  - Verification & Validation (V&V)
  - 오차 및 불확실성 처리 방법
  - 외삽(extrapolation) 및 유사성 평가
  - 문서화 요구사항
- [원문 PDF](https://www.easa.europa.eu/sites/default/files/dfu/proposed_cm-s-014_modelling_simulation_-_for_consultation.pdf)

### FAA

- TAMCSWG (Transport Airplane Metallic and Composite Structures Working Group) — 복합재 피로/손상허용 인증 권고
- Advisory Circular에서 해석 기반 인증 허용 범위 확대 추세
- [FAA 보고서](https://www.faa.gov/sites/faa.gov/files/TAMCSWG_Recommendation_Report_Rev_A.pdf)

### CMH-17

- Volume 3 revision H (2025): 내구성/손상허용, 접합부 설계, 수리 인증 업데이트
- Volume 5 revision B (2026 예정): CMC 데이터셋 추가
- 통계적 허용치 산출에 시뮬레이션 데이터 활용 논의 진행 중

## CerTest 프로젝트 (EU, 2021-2025)

Testing Pyramid를 재구성하는 EU 대형 프로젝트:

| 항목 | 내용 |
|------|------|
| **참여 대학** | Bristol, Bath, Exeter, Southampton |
| **산업 파트너** | Airbus, Rolls Royce, GKN Aerospace, BAE Systems, EASA |
| **기간** | ~2025.8 완료 |
| **목표** | 물리 시험 축소 + 시뮬레이션 확대로 경량/안전/비용효율적 복합재 항공구조 |
| **방법론** | 멀티스케일 통계 모델링 + DoE + **Bayesian Learning** + 하이브리드 시험 플랫폼 |

- [CerTest (EASA)](https://www.easa.europa.eu/en/research-projects/certest)
- [CerTest (Bristol)](https://www.composites-certest.com/)

## Virtual Allowables 논쟁

| 찬성 | 반대 |
|------|------|
| 쿠폰 시험 수천 건 → 시뮬레이션 대체 가능 | BBA 비용의 핵심은 쿠폰이 아닌 component/full-scale 시험 |
| 신소재 도입 속도 가속 | PDA 기반 VA는 상위 스케일에서 더 유용 |
| AI surrogate (ANN, GPE) 기반 빠른 물성 예측 | "시험 대체가 아닌 더 smart한 시험"이 현실적 목표 |

## AI의 역할

- 제한된 시험 데이터로 통계적 허용치(allowables) 생성
- 시험-해석 상관관계(test-analysis correlation) 자동화
- 불확실성 정량화 (Uncertainty Quantification)
- 재료 물성 산포를 반영한 확률론적 수명 예측

### PINN + UQ 최신 동향 (2024-2025)

| 기법 | 특징 | 적용 사례 |
|------|------|---------|
| **Bayesian PINN** | HMC/VI로 posterior 추정, UQ 제공 | 노이즈 데이터에 강건, 과적합 방지 |
| **Multi-fidelity PINN + Transfer Learning** | 저/고충실도 데이터 결합 | 복합재 AE source localization |
| **Theory-Constrained PINN** | 이론적 제약 강화 | 층상 복합재 응력-변형 분석 |

- MDPI Review (2025): "Advancements in PINN for Laminated Composites" — SHM, 구조 해석, 파손 분석, 멀티스케일 모델링 포괄
- PHM Society: "Data-Efficient and Uncertainty-Aware RUL Prediction Using PINN"

### 제조 DT + Right-First-Time

- **IMDEA**: 복합재 생산 공정 실시간 DT 개발
- **NASAMPE 2024**: "Real-Time Material Certification of Composites Using a Digital Twin"
- Closed Loop Manufacturing: 센서 → 공정 모델 → 실시간 보정 → 불량 제거

## Deep Dive (2026-03-13)

### 1. EASA CM-S-014 Credibility Framework — PINN Mapping

EASA's M&S certification framework asks three fundamental questions. PINN + HyBC pipeline addresses all three:

| EASA Requirement | Section | PINN + HyBC Answer |
|-----------------|---------|-------------------|
| **Verification** ("Is the math right?") | Sec. 4 | PINN loss convergence + PDE residual minimization + analytical benchmarks |
| **Validation** ("Does it match reality?") | Sec. 5 | HyBC-derived micro properties validated at coupon level |
| **UQ** ("How wrong could it be?") | Sec. 6 | Bayesian PINN posterior — bottom-up probabilistic chain from constituent level |
| **Extrapolation** | Sec. 7 | Physics constraints + DoE boundary coverage + uncertainty inflation |

Most M&S certification submissions treat material properties as deterministic. Propagating UQ from constituent (fiber/matrix) level through scales is MORE rigorous than what EASA typically sees — a complete traceable credibility chain.

### 2. CerTest vs PINN Fatigue — Complementary Positioning

CerTest (EU, ended 2025) focused on static strength/damage tolerance using traditional FE + Bayesian statistics. **Fatigue degradation remains an open gap** in virtual certification.

Paper-1 Review positioning: CerTest = "state of the art", PINN fatigue = "next step".

See [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3]] for detailed comparison table.

### 3. "Smart Testing" — Not Replacement but Amplification

Virtual Certification is NOT about eliminating tests. It's about making each test a "test multiplier":
- PINN interpolates between tested conditions
- Bayesian UQ identifies which additional test would most reduce uncertainty (Optimal Experimental Design)
- DoE selects minimal representative layup configurations; PINN maps the rest

### Key Insight

> EASA CM-S-014's credibility framework is fully addressable by the PINN + HyBC pipeline: Verification (loss convergence), Validation (coupon-level test comparison), UQ (Bayesian PINN posterior from constituent level). The hardest challenge is Section 7 (Extrapolation) — physics-embedded PINN is inherently more robust than data-only models, but quantitative extrapolation credibility evidence is needed. The "smart testing" paradigm positions PINN as a test multiplier, not a test replacement, aligning with both industry reality and regulatory expectations.

## 관련 노트

- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 인증용 해석의 핵심 방법론
- [[(Concept) Digital Twin Composites|Digital Twin]] — Digital Twin 기반 인증 프레임워크
- [[(Concept) Structural Health Monitoring|SHM]] — Condition-based 인증으로 확장
- [[(Research) Paper-3 PINN Fatigue Degradation|Paper-3: PINN Fatigue Degradation]] — EASA 매핑 상세, DoE 전략
- [[(Research) 포닥 논문 계획|논문 아이디어]] — Paper-1 Review에서 Virtual Cert. 로드맵 제시
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트

## References

1. EASA, "CM-S-014: Modelling & Simulation – CS-25 Structural Certification Specifications", 2020, [easa.europa.eu](https://www.easa.europa.eu/sites/default/files/dfu/proposed_cm-s-014_modelling_simulation_-_for_consultation.pdf)
2. FAA, "TAMCSWG Recommendation Report", [faa.gov](https://www.faa.gov/sites/faa.gov/files/TAMCSWG_Recommendation_Report_Rev_A.pdf)
3. CerTest Project, "Certification for Design: Reshaping the Testing Pyramid", [composites-certest.com](https://www.composites-certest.com/)
4. "Advancements in PINN for Laminated Composites: A Comprehensive Review", Mathematics 13(1), 2025, [mdpi.com](https://www.mdpi.com/2227-7390/13/1/17)
5. "Data-Efficient and Uncertainty-Aware RUL Prediction Using PINN", PHM Society, [phmsociety.org](https://papers.phmsociety.org/index.php/phmconf/article/view/4356)
6. CompositesWorld, "Virtual Testing of Composites: Beyond Make & Break"
7. CompositesWorld, "Accelerating Materials Insertion: Where Do Virtual Allowables Fit?"
