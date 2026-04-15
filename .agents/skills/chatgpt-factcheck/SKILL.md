---
name: chatgpt-factcheck
description: Verify claims and cited links from a ChatGPT share conversation, map the confirmed findings to the user's research notes, and save a structured fact-check note in the vault. Use when the user provides a ChatGPT share URL or asks to audit externally generated research notes before integrating them into Paper-1 or related projects.
---

# ChatGPT Factcheck

Prefer direct source verification over trusting the shared conversation. Save the result as a vault note rather than leaving the audit only in chat.

## Workflow

1. Render or fetch the shared conversation.
2. Extract:
   - claims
   - cited URLs
   - datasets, papers, and institutions mentioned
3. Visit each source and grade the claim:
   - confirmed
   - partial
   - not found
   - unverifiable
4. Read the relevant project note, defaulting to `03-projects/(Research) Paper-1 Review Multiscale Fatigue AI DT.md`, and map which findings matter.
5. Save a structured note in `01-inbox/` with Korean body text and verified links only.

## Output Shape

- `## 개요`
- `## 팩트체크 결과`
- `## 관련 논문 / 데이터셋`
- `## Paper-1 연관성 분석`
- `## Follow-up`

## Guardrails

- Do not cite ChatGPT itself as evidence.
- Mark access-limited or unverifiable sources explicitly.
