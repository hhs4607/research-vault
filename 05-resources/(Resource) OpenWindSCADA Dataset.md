---
title: "OpenWindSCADA — Open Wind Turbine SCADA Dataset Repository"
date: 2026-03-13
tags: [tool/open-source, research/wind-energy, data/scada, research/digital-twin, research/shm]
aliases:
  - "OpenWindSCADA"
  - "풍력 SCADA 데이터셋"
  - "Open Wind SCADA"
description: "풍력 터빈 SCADA 오픈 데이터셋 큐레이션 저장소. 21개 데이터셋, Jupyter 노트북 로더, 커뮤니티 어노테이션 제공. DT/SHM 파이프라인 벤치마킹에 활용."
source: "https://github.com/sltzgs/OpenWindSCADA"
author: "Simon Leszek Effenberger (TU Berlin)"
---

# OpenWindSCADA — Open Wind Turbine SCADA Dataset Repository

## 개요

풍력 터빈 SCADA 오픈 데이터셋을 **큐레이션**하는 저장소. 21개 활성 데이터셋에 대해 고수준 설명, 재사용 가능한 CSV 로더, 데이터 품질/고장 관련 커뮤니티 어노테이션을 제공한다.

## 주요 데이터셋

| 데이터셋 | 위치 | 터빈 수 | 변수 수 | 기간 | 특징 |
|---------|------|--------|--------|------|------|
| **Kelmarsh Farm** ⭐ | UK, 육상 | 6 | ~99 | 5년 | 포괄적 |
| **Penmanshiel Farm** ⭐ | UK, 육상 | 14 | >150 | 5년 | 고해상도 |
| **Hill of Towie** | Scotland | 21 | 655 | 8.7년 | CC-BY-4.0, 업그레이드 문서 포함 |
| **Ørsted Anholt** | Denmark, 해상 | 111 | - | - | NDA 필요 |
| **Dundalk IoT** | Ireland | - | - | 14년 | 장기 연속 모니터링 |

- 총 21개 활성 + 2개 오프라인 데이터셋
- 약 80%가 무료 접근 가능, 일부는 등록/신청 필요
- 샘플링 간격: 1초 ~ 10분

## 제공 기능

### Data Loaders & Visualization (Jupyter Notebooks)
- 자동 CSV 임포트
- Power curve 플롯
- Wind rose 다이어그램
- 시간별 데이터 가용성 추적
- 터빈별 "Overview Cockpit" 대시보드

### Community Annotations
- 신호 이상/고장 기록 (CSV 기반)
- 타임스탬프 (시작/종료)
- SCADA 로그 메시지 연결
- 사용자 비고 (peer discovery용)

## 사용법

```bash
git clone https://github.com/sltzgs/OpenWindSCADA
# 각 데이터셋 소스에서 CSV 다운로드 → /data 폴더에 배치
# /notebooks 디렉토리의 Jupyter 노트북 실행
```

## 관련 논문

- **Primary**: Effenberger & Ludwig (2022), "A collection and categorization of open-source wind and wind power datasets", *Wind Energy* 25(10): 1659-1683, [DOI: 10.1002/we.2766](https://onlinelibrary.wiley.com/doi/full/10.1002/we.2766)
- Marti-Puig et al. (2024), wind turbine database for intelligent O&M, *Scientific Data*
- **관련 이니셔티브**: [IEA Task 43 Open Data](https://iea-wind.org/task43/task-43-open-data/)

## 저장소 정보

- **Stars**: 207 / **Forks**: 38 / **Commits**: 67
- **라이선스**: GPL-3.0
- **기술 스택**: Jupyter Notebook (99.9%), Python (0.1%)
- **연락처**: simon.leszek@tu-berlin.de

## 복합재 연구와의 연결

- SCADA 데이터 = 풍력 블레이드(복합재)의 운용 하중 이력
- Digital Twin 파이프라인 개발/검증용 벤치마크 데이터로 활용 가능
- wtDigiTwin과 조합하여 피로 수명 예측 파이프라인 프로토타이핑
- 복합재 구조물 SHM 데이터 분석 방법론 개발의 참조 사례

## Deep Dive (2026-03-13)

Not directly applicable at current research stage. Potential future use:
- SCADA data as realistic load spectra input for PINN fatigue model validation
- OpenWindSCADA + wtDigiTwin as proof-of-concept DT pipeline before composite-specific implementation

## 관련 노트

- [[(Resource) wtDigiTwin NREL|wtDigiTwin]] — 이 데이터셋으로 DT 파이프라인 벤치마킹
- [[(Concept) Digital Twin Composites|Digital Twin]] — DT 개발에 SCADA 데이터 활용
- [[(Concept) Structural Health Monitoring|SHM]] — SCADA = SHM 데이터의 일종
- [[(Paper) Lillgrund Probabilistic Lifetime Extension|Lillgrund 수명 연장 연구]] — 관련 풍력단지 연구
- [[(Research) 2026 박사후 국내연수|2026 박사후 국내연수]] — 연구 프로젝트
