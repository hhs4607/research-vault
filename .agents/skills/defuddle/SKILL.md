---
name: defuddle
description: "[DEPRECATED 2026-04-15 — CLI missing] Use WebFetch instead. 복구: npm i -g defuddle-cli"
status: deprecated-broken
deprecated_at: 2026-04-15
redirect: "WebFetch (built-in tool)"
recovery: "npm install -g defuddle-cli && which defuddle"
---

**⚠️ DEPRECATED** — CLI 미설치 감지 (2026-04-15). `WebFetch` 사용. 복구 원할 시 위 `recovery` 명령 실행 후 이 frontmatter `status:` 제거.

---

# Defuddle

Use Defuddle CLI to extract clean readable content from web pages. Prefer over WebFetch for standard web pages — it removes navigation, ads, and clutter, reducing token usage.

If not installed: `npm install -g defuddle`

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |
