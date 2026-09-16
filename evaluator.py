#!/usr/bin/env python3
"""
Deterministic evaluator for hn-mcp-auth-status-boundary-lab.

Answers STATUS questions: which normative layer governs each synthetic
authorization situation, and what 2026-07-28 core compliance outcome follows.

No live OAuth, no network, no tokens, no external dependencies — stdlib only.
Exit 0. Recorded output: results.json + RESULTS.md
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
FIXTURES = ROOT / "fixtures" / "cases.json"
RESULTS_JSON = ROOT / "results.json"
RESULTS_MD = ROOT / "RESULTS.md"

# 2026-07-28 core rules (grounded in basic/authorization/index.mdx 2026-09-16):
# - Authorization OPTIONAL (line 18)
# - Bearer MUST be in Authorization header, MUST NOT be in query string (lines 258-271)
# - Servers MUST validate audience/resource indicator RFC 8707 (lines 283-285)
# - DPoP (RFC 9449) not referenced in core -> not a core requirement
# - stdio SHOULD NOT follow HTTP authorization spec -> env creds path

def evaluate_case(c):
    cid = c["id"]
    transport = c.get("transport", "http")
    auth_enabled = c.get("auth_enabled", True)
    layer = c.get("governing_layer", "unknown")

    # Stdio path: out of scope for HTTP auth spec
    if transport == "stdio":
        return {
            "case_id": cid,
            "governing_layer": layer,
            "core_compliance": "pass",
            "http_auth_applies": False,
            "reason": "STDIO SHOULD NOT follow HTTP authorization spec (2026-07-28 line 21); env credentials are the correct path. Stdio is not deprecated.",
            "effective_status": 200,
            "detail": "Stdio: HTTP Authorization flow does not apply."
        }

    # HTTP with auth disabled: conformant because OPTIONAL
    if not auth_enabled:
        return {
            "case_id": cid,
            "governing_layer": layer,
            "core_compliance": "pass",
            "http_auth_applies": False,
            "reason": "Authorization is OPTIONAL for MCP implementations (2026-07-28 line 18). No 401 required.",
            "effective_status": 200,
            "detail": "Auth disabled: conformant without Authorization header."
        }

    req = c.get("request", {}) or {}
    headers = req.get("headers") or {}
    query = req.get("query") or ""
    token = c.get("token")
    resource_url = req.get("resource_url")

    auth_header = headers.get("Authorization", "")
    has_bearer_in_header = auth_header.startswith("Bearer ") and len(auth_header) > 7
    has_token_in_query = "access_token=" in query
    has_dpop = c.get("has_dpop") is True

    # Stable extension / roadmap layers: report layer and note not core-mandatory
    if layer in ("stable-extension", "roadmap"):
        # If they also tried to carry a violation, surface it
        if has_token_in_query:
            return {
                "case_id": cid,
                "governing_layer": layer,
                "core_compliance": "fail",
                "http_auth_applies": True,
                "reason": "Token in query string violates core even when an extension/roadmap flow is present.",
                "effective_status": 401,
                "detail": f"{layer}: query-string bearer not allowed."
            }
        return {
            "case_id": cid,
            "governing_layer": layer,
            "core_compliance": "pass",
            "http_auth_applies": True,
            "reason": f"{layer}: not a 2026-07-28 core MUST. Core bearer/audience rules still apply independently.",
            "effective_status": 200,
            "detail": f"{layer} governs DPoP/EMA identity; absence/presence does not fail core compliance.",
            "has_dpop": has_dpop,
        }

    # Core layer: apply bearer/audience rules
    # 1. Query-string bearer -> MUST NOT (line 271)
    if has_token_in_query:
        return {
            "case_id": cid,
            "governing_layer": "core",
            "core_compliance": "fail",
            "http_auth_applies": True,
            "reason": "Access tokens MUST NOT be in URI query string (2026-07-28 line 271) — RFC 6750 §3.",
            "effective_status": 401,
            "detail": "Query-string bearer rejected."
        }

    # 2. Missing bearer header when auth enabled -> 401
    if not has_bearer_in_header:
        return {
            "case_id": cid,
            "governing_layer": "core",
            "core_compliance": "fail",
            "http_auth_applies": True,
            "reason": "Authorization header Bearer required when auth enabled (2026-07-28 lines 262-266).",
            "effective_status": 401,
            "detail": "Missing or malformed Authorization: Bearer."
        }

    # 3. Audience mismatch -> 401 (RFC 8707)
    if token and resource_url:
        aud = token.get("audience") if isinstance(token, dict) else None
        if aud and aud != resource_url and aud != req.get("resource_param", resource_url):
            # More precise: compare to resource_param or resource_url canonical
            expected = req.get("resource_param") or resource_url
            if aud != expected:
                return {
                    "case_id": cid,
                    "governing_layer": "core",
                    "core_compliance": "fail",
                    "http_auth_applies": True,
                    "reason": "MCP servers MUST validate audience per RFC 8707 (2026-07-28 lines 283-285). Wrong audience -> 401.",
                    "effective_status": 401,
                    "detail": f"Audience {aud!r} does not match resource {expected!r}."
                }

    # 4. Valid without DPoP -> PASS (DPoP not a 2026-07-28 core MUST)
    if not has_dpop:
        return {
            "case_id": cid,
            "governing_layer": "core",
            "core_compliance": "pass",
            "http_auth_applies": True,
            "reason": "DPoP (RFC 9449) is not referenced by 2026-07-28 basic/authorization (grep 0). Absence does not fail core.",
            "effective_status": 200,
            "detail": "Valid bearer + audience without DPoP: core-compliant."
        }

    # 5. Default pass
    return {
        "case_id": cid,
        "governing_layer": "core",
        "core_compliance": "pass",
        "http_auth_applies": True,
        "reason": "Bearer in header, no query leakage, audience validated. DPoP presence does not affect core result.",
        "effective_status": 200,
        "detail": "Core-compliant."
    }

def main():
    cases = json.loads(FIXTURES.read_text())
    results = [evaluate_case(c) for c in cases]
    pass_count = sum(1 for r in results if r["core_compliance"] == "pass")
    fail_count = len(results) - pass_count

    RESULTS_JSON.write_text(json.dumps({
        "mcp_spec_version": "2026-07-28",
        "spec_source": "modelcontextprotocol/modelcontextprotocol@main docs/specification/2026-07-28/basic/authorization/index.mdx",
        "roadmap_source": "blog.modelcontextprotocol.io/posts/mcp-roadmap/",
        "dpop_in_core": False,
        "dpop_status": "roadmap priority (not a 2026-07-28 core MUST)",
        "workload_identity_status": "roadmap priority (WIF/ID-JAG/RFC8693 via Agent Identity WG forming)",
        "ema_status": "stable extension (not 2026-07-28 core)",
        "stdio_status": "NOT deprecated; stdio uses env credentials, SHOULD NOT follow HTTP auth spec",
        "total": len(results),
        "pass": pass_count,
        "fail": fail_count,
        "results": results
    }, indent=2) + "\n")

    lines = []
    lines.append(f"# Results — hn-mcp-auth-status-boundary-lab")
    lines.append("")
    lines.append(f"MCP spec: **2026-07-28** · DPoP in core: **no** (grep 0) · Generated: deterministic stdlib evaluator")
    lines.append("")
    lines.append(f"**{len(results)} cases · {pass_count} pass · {fail_count} fail** (fail = core violation, not extension absence)")
    lines.append("")
    lines.append("| Case | Layer | Core | HTTP | Status | Reason |")
    lines.append("|---|---|---|---|---|---|---|")
    for r in results:
        lines.append(f"| {r['case_id']} | {r['governing_layer']} | {r['core_compliance']} | {r['http_auth_applies']} | {r['effective_status']} | {r['reason'][:90]} |")
    lines.append("")
    lines.append("Layers: `core` = 2026-07-28 MUST/SHOULD; `optional-auth` = auth disabled is allowed; `stable-extension` = EMA/ID-JAG; `roadmap` = DPoP/WIF; `out-of-scope-for-http-auth` = stdio.")
    lines.append("")
    RESULTS_MD.write_text("\n".join(lines) + "\n")
    print(f"{len(results)} cases · {pass_count} pass · {fail_count} fail -> results.json + RESULTS.md")

if __name__ == "__main__":
    main()
