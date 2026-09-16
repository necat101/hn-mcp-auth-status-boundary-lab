# Results — hn-mcp-auth-status-boundary-lab

MCP spec: **2026-07-28** · DPoP in core: **no** (grep 0) · Generated: deterministic stdlib evaluator

**8 cases · 6 pass · 2 fail** (fail = core violation, not extension absence)

| Case | Layer | Core | HTTP | Status | Reason |
|---|---|---|---|---|---|---|
| http-auth-disabled | optional-auth | pass | False | 200 | Authorization is OPTIONAL for MCP implementations (2026-07-28 line 18). No 401 required. |
| valid-bearer-header | core | pass | True | 200 | DPoP (RFC 9449) is not referenced by 2026-07-28 basic/authorization (grep 0). Absence does |
| token-in-query-string | core | fail | True | 401 | Access tokens MUST NOT be in URI query string (2026-07-28 line 271) — RFC 6750 §3. |
| wrong-audience | core | fail | True | 401 | MCP servers MUST validate audience per RFC 8707 (2026-07-28 lines 283-285). Wrong audience |
| valid-without-dpop | core | pass | True | 200 | DPoP (RFC 9449) is not referenced by 2026-07-28 basic/authorization (grep 0). Absence does |
| ema-stable-extension | stable-extension | pass | True | 200 | stable-extension: not a 2026-07-28 core MUST. Core bearer/audience rules still apply indep |
| dpop-roadmap | roadmap | pass | True | 200 | roadmap: not a 2026-07-28 core MUST. Core bearer/audience rules still apply independently. |
| stdio-env-creds | out-of-scope-for-http-auth | pass | False | 200 | STDIO SHOULD NOT follow HTTP authorization spec (2026-07-28 line 21); env credentials are  |

Layers: `core` = 2026-07-28 MUST/SHOULD; `optional-auth` = auth disabled is allowed; `stable-extension` = EMA/ID-JAG; `roadmap` = DPoP/WIF; `out-of-scope-for-http-auth` = stdio.

