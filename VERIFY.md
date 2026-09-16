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
