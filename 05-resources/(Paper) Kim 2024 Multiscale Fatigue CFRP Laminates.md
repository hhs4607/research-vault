---
title: "Kim 2024: CFRP 라미네이트의 다중스케일 피로 수명 예측 모델 — 구성재료 물성 저하 및 기지재 국부 응력 집중 고려"
date: 2024-01-01
tags: [research/fatigue, research/multiscale, engineering/composites, research/cdm]
aliases: [Kim 2024 CFRP fatigue, multiscale fatigue CFRP]
description: "CFRP 라미네이트의 인장-인장 피로 수명을 다중스케일로 예측하는 모델. Mori-Tanaka 평균장 이론 기반으로 구성재료(섬유/기지재)의 물성 저하와 기지재 국부 응력 집중을 함께 고려한다."
source: "https://doi.org/10.1016/j.compstruct.2024.118519"
---

# Multiscale fatigue life prediction model for CFRP laminates considering the mechanical degradation of its constituents and the local stress concentration of the matrix

## 서지 정보

| 항목 | 내용 |
|------|------|
| **저자** | Jeong Hwan Kim, Dongwon Ha, Hoil Choi, Gun Jin Yun |
| **소속** | Seoul National University, Aerospace Structures And Materials Laboratory (ASML) |
| **저널** | *Composite Structures*, Volume 349, Article 118519 |
| **연도** | 2024 |
| **DOI** | [10.1016/j.compstruct.2024.118519](https://doi.org/10.1016/j.compstruct.2024.118519) |

## 핵심 내용

CFRP 라미네이트의 **인장-인장 사이클 하중** 하에서 피로 수명을 예측하는 다중스케일 모델을 제안한다.

### 핵심 메커니즘 2가지

1. **구성재료의 기계적 물성 저하 (Mechanical Degradation)**
   - 섬유(fiber)와 기지재(matrix) 각각의 피로에 따른 강성/강도 저하를 모델링
   - Mori-Tanaka 평균장 이론(mean-field homogenization)으로 micro → macro 스케일 브릿징

2. **기지재 국부 응력 집중 (Local Stress Concentration)**
   - 섬유-기지재 계면에서 발생하는 응력 집중 효과를 반영
   - 매크로 레벨의 평균 응력만으로는 포착할 수 없는 국부 파손 메커니즘 고려

### 방법론

- **Mori-Tanaka 평균장 이론**: 각 상(phase)의 재료 물성 저하를 효율적으로 다중스케일 해석에 반영
- 사이클별로 구성재료 물성을 업데이트하며 점진적 손상을 추적
- 라미네이트 레벨의 피로 수명을 구성재료 레벨 파라미터로부터 예측

## 관련 노트

- [[(Paper) Choi 2025 Multiscale Bayesian Fatigue|Choi et al. 2025]] — 본 논문의 후속 연구. 같은 프레임워크에 베이지안 불확실성 정량화를 추가
- [[(Concept) Multiscale Fatigue Analysis|Multiscale Fatigue Analysis]] — 공통 방법론
- [[(Resource) Transformer Fatigue 구현 방법 기획|Transformer Fatigue 구현 기획]] — 피로 수명 예측 대안 접근법
