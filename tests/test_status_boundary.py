"""
Independent oracle: re-derives expected status from fixture facts without
calling evaluator.evaluate_case. Fails if any of the five misreading classes
would slip through.
"""
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parent.parent
FIXTURES = ROOT / "fixtures" / "cases.json"
sys.path.insert(0, str(ROOT))
import evaluator as ev


def oracle(c):
    """Independent derivation from raw fixture fields."""
    transport = c.get("transport", "http")
    auth_enabled = c.get("auth_enabled", True)
    layer = c.get("governing_layer")
    req = c.get("request") or {}
    headers = req.get("headers") or {}
    query = req.get("query") or ""
    token = c.get("token")

    if transport == "stdio":
        return ("pass", "out-of-scope-for-http-auth", False)
    if not auth_enabled:
        return ("pass", "optional-auth", False)
    # query-string bearer always fails core regardless of layer
    if "access_token=" in query:
        return ("fail", "core", True)
    # audience mismatch fails core
    if token and isinstance(token, dict):
        aud = token.get("audience")
        expected = req.get("resource_param") or req.get("resource_url")
        if aud and expected and aud != expected:
            return ("fail", "core", True)
    # missing Authorization header when auth enabled -> fail (unless layer already exempts, handled above)
    auth = headers.get("Authorization", "")
    if not (auth.startswith("Bearer ") and len(auth) > 7):
        # stdio/disabled already returned
        return ("fail", "core", True)
    # extensions/roadmap: presence/absence of DPoP must NOT flip core pass->fail
    if layer in ("stable-extension", "roadmap"):
        return ("pass", layer, True)
    # valid without DPoP -> pass (DPoP not core-mandatory)
    return ("pass", "core", True)


class TestStatusBoundary(unittest.TestCase):
    def test_all_cases_have_required_distinctions(self):
        cases = json.loads(FIXTURES.read_text())
        ids = {c["id"] for c in cases}
        for must in [
            "http-auth-disabled",
            "valid-bearer-header",
            "token-in-query-string",
            "wrong-audience",
            "valid-without-dpop",
            "ema-stable-extension",
            "dpop-roadmap",
            "stdio-env-creds",
        ]:
            self.assertIn(must, ids, f"Missing required fixture: {must}")

    def test_evaluator_matches_oracle(self):
        cases = json.loads(FIXTURES.read_text())
        for c in cases:
            exp_compliance, exp_layer, exp_http_applies = oracle(c)
            got = ev.evaluate_case(c)
            with self.subTest(case=c["id"]):
                self.assertEqual(got["core_compliance"], exp_compliance,
                    f"{c['id']}: core_compliance mismatch (got {got})")
                self.assertEqual(got["governing_layer"], exp_layer,
                    f"{c['id']}: governing_layer mismatch")
                self.assertEqual(got["http_auth_applies"], exp_http_applies,
                    f"{c['id']}: http_auth_applies mismatch")

    def test_optional_auth_not_mandatory(self):
        """Auth disabled must be PASS — evaluator must not treat OPTIONAL as MUST."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "http-auth-disabled")
        r = ev.evaluate_case(c)
        self.assertEqual(r["core_compliance"], "pass")
        self.assertEqual(r["governing_layer"], "optional-auth")

    def test_dpop_not_mandatory_in_core(self):
        """Valid without DPoP must be PASS — DPoP is not a 2026-07-28 core MUST."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "valid-without-dpop")
        r = ev.evaluate_case(c)
        self.assertEqual(r["core_compliance"], "pass")
        self.assertEqual(r["governing_layer"], "core")
        self.assertFalse(c.get("has_dpop"))

    def test_roadmap_dpop_not_standardized(self):
        """DPoP/workload case is roadmap layer; core_compliance must still be pass (roadmap != fail)."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "dpop-roadmap")
        r = ev.evaluate_case(c)
        self.assertEqual(r["governing_layer"], "roadmap")
        self.assertEqual(r["core_compliance"], "pass")

    def test_ema_is_stable_extension_not_core(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "ema-stable-extension")
        r = ev.evaluate_case(c)
        self.assertEqual(r["governing_layer"], "stable-extension")
        self.assertEqual(r["core_compliance"], "pass")

    def test_http_native_not_every_scheme(self):
        """Query-string bearer must FAIL — HTTP-native does not bless every HTTP auth placement."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "token-in-query-string")
        r = ev.evaluate_case(c)
        self.assertEqual(r["core_compliance"], "fail")
        self.assertEqual(r["effective_status"], 401)

    def test_stdio_not_deprecated(self):
        """Stdio must be out-of-scope-for-http-auth and PASS (env creds, not Authorization)."""
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "stdio-env-creds")
        r = ev.evaluate_case(c)
        self.assertEqual(r["governing_layer"], "out-of-scope-for-http-auth")
        self.assertEqual(r["core_compliance"], "pass")
        self.assertFalse(r["http_auth_applies"])

    def test_wrong_audience_fails(self):
        c = next(x for x in json.loads(FIXTURES.read_text()) if x["id"] == "wrong-audience")
        r = ev.evaluate_case(c)
        self.assertEqual(r["core_compliance"], "fail")
        self.assertEqual(r["effective_status"], 401)


if __name__ == "__main__":
    unittest.main()
