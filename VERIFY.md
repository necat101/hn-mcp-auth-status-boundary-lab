# Verification — fresh unauthenticated HTTPS clone

Date (UTC): 2026-09-16T18:46:47Z  
Repo: https://github.com/necat101/hn-mcp-auth-status-boundary-lab  
Implementation revision (tested): `9cd072e8f6e927a089a77447e08c0770223c05c9`  
Clone origin: `https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git` (public HTTPS, not file://)

```
$ rm -rf /tmp/fresh-lab && git clone https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git /tmp/fresh-lab
Cloning into '/tmp/fresh-lab'...

$ git -C /tmp/fresh-lab rev-parse HEAD
9cd072e8f6e927a089a77447e08c0770223c05c9

$ git -C /home/ubuntu/.openclaw/workspace/hn-mcp-auth-status-boundary-lab rev-parse HEAD
9cd072e8f6e927a089a77447e08c0770223c05c9
=> MATCH (fresh clone revision == local implementation revision)

$ cd /tmp/fresh-lab && python3 evaluator.py
8 cases · 6 pass · 2 fail -> results.json + RESULTS.md

$ python3 -m unittest tests/test_status_boundary.py -v
test_all_cases_have_required_distinctions ... ok
test_dpop_not_mandatory_in_core ... ok
test_ema_is_stable_extension_not_core ... ok
test_evaluator_matches_oracle ... ok
test_http_native_not_every_scheme ... ok
test_optional_auth_not_mandatory ... ok
test_roadmap_dpop_not_standardized ... ok
test_stdio_not_deprecated ... ok
test_wrong_audience_fails ... ok
----------------------------------------------------------------------
Ran 9 tests in 0.010s
OK
```

GitHub Actions: https://github.com/necat101/hn-mcp-auth-status-boundary-lab/actions/runs/35136301416 — `ci` completed `success` on `9cd072e`.

---

## Second fresh-clone check — documentation revision 58c6d3c

This section records the state after the documentation revision was public.
It does not re-execute the lab; only HEAD/clone-ancestry checks.

- Public HTTPS origin: https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git
- Expected published HEAD (documentation revision): 58c6d3c9e0846f1823c12b5ff2761a7b40993f21
- Fresh clone HEAD (unauthenticated HTTPS, `git clone https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git /tmp/fresh-lab`): 58c6d3c9e0846f1823c12b5ff2761a7b40993f21
- Equality: MATCH
- Implementation revision actually execution-tested in a fresh clone: 9cd072e8f6e927a089a77447e08c0770223c05c9 (`python3 evaluator.py` → 8 cases · 6 pass · 2 intentional fail; `python3 -m unittest tests/test_status_boundary.py -v` → 9 tests OK) — see Section 1 transcript above. The documentation commit 58c6d3c itself was not separately execution-tested; only its HEAD/clone presence was verified. GitHub Actions for the new evidence-repair commit 3bcdf04d4186b5b6cd9c62af3453107f4e22dbd2 will be inspected separately (fresh-clone HEAD for that commit appended below after push).


---

## Third fresh-clone check — evidence-repair revision 71e86d2 (2026-09-16T18:59Z)

- Public HTTPS origin: https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git
- Expected published HEAD: 71e86d2f4558ef470a4f1e95d8107f33a522e32b
- Fresh clone HEAD (unauthenticated HTTPS): 71e86d2f4558ef470a4f1e95d8107f33a522e32b
- Equality: MATCH
- Implementation revision actually execution-tested: 9cd072e8f6e927a089a77447e08c0770223c05c9 content (evaluator/fixtures/tests unchanged since that commit; verified in this fresh clone: `python3 evaluator.py` → 8 cases · 6 pass · 2 intentional core-rule fail; `python3 -m unittest tests/test_status_boundary.py -v` → 9 tests OK). The evidence-repair/documentation commits (3bcdf04, 71e86d2) modify only README.md and VERIFY.md and were verified for HEAD/clone presence, not separately counted as a new lab execution revision.
- Clone command: `git clone https://github.com/necat101/hn-mcp-auth-status-boundary-lab.git /tmp/fresh-final` (public, not file://)
- Note: 9cd072e remains an ancestor of 71e86d2 (`git log --oneline` shows 9cd072e → 58c6d3c → 3bcdf04 → 71e86d2); evaluator output identical on rerun from fresh clone.
