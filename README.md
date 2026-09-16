# hn-mcp-auth-status-boundary-lab

Small, deterministic evidence lab for [**HN 49399591 — “New MCP Roadmap”**](https://news.ycombinator.com/item?id=49399591) → [blog.modelcontextprotocol.io/posts/mcp-roadmap/](https://blog.modelcontextprotocol.io/posts/mcp-roadmap/) and **MCP 2026-07-28**.

Tests the platform-team claim:

> “MCP 2026-07-28 standardized DPoP and workload identity for remote servers, bearer-only OAuth is basically legacy now, and stdio is on the way out.”

**Verdict: the claim conflates four distinct normative layers.** The lab separates them and checks each case against the layer that actually governs it.

## Boundary under test

| Layer | Meaning | Source |
|---|---|---|
| **2026-07-28 core requirement** | Normative `MUST`/`SHOULD` in `docs/specification/2026-07-28/basic/authorization` | `basic/authorization/index.mdx` (fetched 2026-09-16) |
| **Optional authorization** | Whole authorization section is `OPTIONAL` for MCP implementations | same file line 18: “Authorization is **OPTIONAL**” |
| **Stable extension** | `Enterprise-Managed Authorization` — described as “now stable” in the 2026-07-28 cycle post | blog post 2026-07-28 section + `extensions/auth/enterprise-managed-authorization` |
| **Roadmap priority** | DPoP finalization, WIF / ID-JAG / RFC 8693 agent-identity tracks | `blog.modelcontextprotocol.io/posts/mcp-roadmap/` § Agent identity and enterprise-ready security |

Rule: **roadmap wording ≠ current normative requirement.** Every status answer must cite the layer that actually mandates it.

## What 2026-07-28 core actually says (verified 2026-09-16)

- Authorization is **OPTIONAL**. When present, HTTP `SHOULD` conform; **stdio `SHOULD NOT` follow this spec** and must retrieve credentials from the environment instead (lines 18-21). Stdio is not deprecated.
- No normative reference to **RFC 9449 (DPoP)** in `basic/authorization/index.mdx` (`grep -c DPoP` = 0). DPoP is future work.
- Bearer token **MUST** be sent in `Authorization: Bearer <token>` per OAuth 2.1 §5.1.1 and **MUST NOT** be in the query string (lines 258-271).
- Servers **MUST** validate audience via Resource Indicators **RFC 8707** (`resource` param, canonical URI) and reject wrong-audience tokens with 401 (lines 283-289).
- The remote server “now no different from any other HTTP workload” refers to **hosting/operation** (stateless, no protocol sessions), not to relaxing the bearer/audience rules above.

## HN 49399591 audit (comments actually retrieved — via HN Firebase + Algolia)

Quoted text is abbreviated; IDs and authors are exact so you can re-fetch `https://hacker-news.firebaseio.com/v0/item/<id>.json`.

| # | Proposition seen on thread | Source | Assessment |
|---|---|---|---|
| 1 | “With the 2026-07-28 release, a remote MCP server is now no different from any other HTTP workload” — MCP becomes ordinary HTTP. | **rco8786 · 49400071** (top-level, paraphrases roadmap heading `HTTP-native transport unification and hardening`) | **Partially true, easily overstretched.** The line is real and about *operability* (stateless, horizontal scale, std headers/status codes). It does **not** imply every ordinary HTTP auth scheme is conformant — the Bearer/audience rules above still apply. Footgun 4 tests this. |
| 2 | The roadmap’s agent-identity paragraph (browser-person → pillar) is quoted verbatim; several replies treat it as the near-term authorization target. | **izend · 49400011** (quotes roadmap’s *Agent identity and enterprise-ready security* paragraph at length) | **Roadmap, not 2026-07-28 core.** The paragraph lists *future* DPoP finalization, WIF/ID-JAG/RFC 8693 — none are in `basic/authorization/index.mdx`. |
| 3 | “The work here covers finalizing Demonstrating Proof of Possession (DPoP) and driving its adoption…” — DPoP talk triggers the “already standardized” reading. | **izend · 49400011** quoting roadmap; corroborated by `posts/mcp-roadmap` § DPoP bullet | **Roadmap priority.** `finalizing` + `driving adoption` + `Agent Identity WG (forming)` = not yet a 2026-07-28 core `MUST`. |
| 4 | “It's unreal how bad the initial rollout was between HTTP/streaming and stdio, bearer auth and OAuth. Virtually every client/MCP server pair had a different portion of that matrix implemented.” — fragmentation across the rollout matrix. | **colingauvin · 49400633** (verbatim: HTTP/streaming, stdio, bearer auth, OAuth; inconsistent client/server support) | **Fragmentation was real, but the comment does not state bearer-only is legacy.** 2026-07-28 *standardizes* on `Authorization: Bearer` + RFC 8707/9728/9207 — bearer is the stable core, not legacy. |
| 5 | Skepticism that workload identity is settled: two sub-threads debate enterprise patterns vs DPoP. | **gz5 · 49400383** (“two streams… RFC 7523/OIDC vs DPoP”) ; **bandofthehawk · 49400223** (“use agentgateway as auth proxy”) | **Both patterns are roadmap work.** The thread itself frames them as alternatives/divergence — consistent with spec gap (no DPoP normative text in 2026-07-28). The claim that 2026-07-28 “standardized” either pattern is not supported. |
| 6 | “Is stdio being deprecated? I couldn't tell from this page” | **ihuman · 49401110** (verbatim question on the roadmap page) | **Directly asked on thread; answer is no on current spec.** `basic/authorization` line 21 says stdio `SHOULD NOT` use HTTP auth and `basic/transports/stdio.mdx` remains fully specified; the roadmap proposes `HTTP over stdio` unification (HTTP/2 multiplexing while retaining subprocess guarantees), not removal. Current stdio support plus the proposed unification does not establish that stdio is deprecated; it also does not prove that stdio's transport shape will remain unchanged indefinitely. |

If a comment you need is missing above, fetch it directly — these are not invented.

## Lab design

Pure **Python stdlib + shell**, no live OAuth, no network, no tokens, no external packages. Every situation is a synthetic JSON fixture; the evaluator answers a *status question* (“which layer governs this, and what does 2026-07-28 require?”), not “would this product pass certification?”

### Fixtures (`fixtures/cases.json`)

Eight synthetic cases — each carries the facts the evaluator must interpret:

1. `http-auth-disabled` — HTTP, authorization disabled entirely
2. `valid-bearer-header` — valid bearer in `Authorization` header, correct audience
3. `token-in-query-string` — token placed in `?access_token=`
4. `wrong-audience` — valid token for a different MCP resource
5. `valid-without-dpop` — otherwise-valid baseline without DPoP proof
6. `ema-stable-extension` — Enterprise-Managed Authorization / ID-JAG (stable extension)
7. `dpop-roadmap` — DPoP / workload-identity proof-of-possession (roadmap-only)
8. `stdio-env-creds` — stdio credentials via environment, no HTTP Authorization flow

### Evaluator (`evaluator.py`)

`python3 evaluator.py` reads `fixtures/cases.json`, maps each case to the **governing layer** (`core` / `optional-auth` / `stable-extension` / `roadmap` / `out-of-scope-for-http-auth`), and applies 2026-07-28 core rules (optional flag, bearer-in-header, no-query, audience binding). Exit 0; writes `results.json` with `pass/fail` per case and a human `RESULTS.md`.

### Tests (`tests/test_status_boundary.py`)

Independent oracle — re-derives the expected status from fixture facts without calling the evaluator’s decision function. Catches:

- treating optional MCP authorization as mandatory for every implementation
- treating DPoP as a mandatory 2026-07-28 core requirement
- treating roadmap agent-identity work as already standardized
- treating “HTTP-native” as proof that every ordinary HTTP auth scheme is MCP-conformant
- treating stdio as deprecated because its credential handling differs from HTTP

```
python3 -m unittest tests/test_status_boundary.py -v
```

### Verification

```sh
./verify.sh            # local deterministic evaluator/test check
cat RESULTS.md         # recorded actual output
cat VERIFY.md          # public HTTPS fresh-clone transcript (see VERIFY.md for the public-origin procedure)
```

## Quick start

```sh
git clone https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git
cd hn-mcp-auth-status-boundary-lab
python3 evaluator.py
python3 -m unittest tests/test_status_boundary.py -v
./verify.sh
```

## Sources inspected 2026-09-16

- HN item `49399591` + kids via `hacker-news.firebaseio.com` and `hn.algolia.com/api/v1/items/49399591` (IDs above)
- `blog.modelcontextprotocol.io/posts/mcp-roadmap/` (New MCP Roadmap)
- `modelcontextprotocol/modelcontextprotocol` @ `main` — `docs/specification/2026-07-28/basic/authorization/index.mdx` (grep: no `DPoP`), `docs/specification/2026-07-28/basic/transports/stdio.mdx`, `docs/development/roadmap.mdx`
- RFCs cited by the spec: **RFC 6750** (Bearer), **RFC 8707** (Resource Indicators), **RFC 9449** (DPoP — not referenced by 2026-07-28, roadmap-only)

## Result snapshot (actual, 2026-09-16 — corrected)

Fixture/core-compliance outcome (evaluator `results.json` / `RESULTS.md`):

```
8 cases · 6 pass · 2 intentional core-rule fail  (see RESULTS.md)
  pass: http-auth-disabled, valid-bearer-header, valid-without-dpop, ema-stable-extension, dpop-roadmap, stdio-env-creds
  fail (intentional rejections per 2026-07-28 core rules): token-in-query-string (MUST NOT in query, line 271), wrong-audience (MUST validate audience per RFC 8707, lines 283-285)
```

Unit-test result (independent oracle, not fixture count):

```
9 tests OK — python3 -m unittest tests/test_status_boundary.py -v
```

Status conclusions (unchanged):

```
DPoP: roadmap priority (not a 2026-07-28 core MUST)
Agent/workload identity (WIF/ID-JAG/RFC 8693): roadmap priority
Enterprise-Managed Authorization: stable extension (not 2026-07-28 core)
Stdio: NOT deprecated; SHOULD NOT use HTTP Authorization, uses environment credentials
```

## License

MIT
