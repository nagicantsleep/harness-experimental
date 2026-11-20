import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
SCRIPT = ROOT / ".agents/skills/guardrails/tools/check_architecture.py"
FIX = HERE / "fixtures"


def run(*extra, cfg=FIX / "config.json"):
    p = subprocess.run([sys.executable, str(SCRIPT), "--config", str(cfg), "--root", str(FIX), "--json", *extra], capture_output=True, text=True)
    return p.returncode, (json.loads(p.stdout) if p.stdout.strip().startswith("[") else p.stdout)


class CheckArchitecture(unittest.TestCase):
    def setUp(self):
        self.code, self.found = run()
        self.keys = {(v["path"], v["rule"]) for v in self.found}

    def has(self, path, rule):
        return (path, rule) in self.keys

    def test_exit_code_nonzero(self):
        self.assertEqual(self.code, 1)

    def test_ts_layer_violation(self):
        self.assertTrue(self.has("src/domain/order.ts", "layer-domain-must-not-import-infra"))

    def test_ts_alias_resolves(self):
        self.assertFalse(self.has("src/ui/panel.ts", "layer-ui-must-not-import-domain"))

    def test_python_layer_by_namespace(self):
        self.assertFalse(self.has("src/domain/svc.py", "layer-domain-must-not-import-infra"))

    def test_csharp_namespace_layer(self):
        self.assertTrue(self.has("src/domain/Svc.cs", "layer-domain-must-not-import-infra"))

    def test_gdscript_res_path(self):
        self.assertTrue(self.has("game/core/rules.gd", "layer-gcore-must-not-import-gscenes"))

    def test_banned_regex(self):
        self.assertTrue(self.has("src/ui/panel.ts", "no-set-timeout"))

    def test_justifying_comments_all_langs(self):
        for p in ("src/ui/panel.ts", "src/domain/svc.py", "src/domain/Svc.cs", "game/core/rules.gd"):
            self.assertTrue(self.has(p, "no-justifying-comments"), p)

    def test_url_and_string_hash_are_not_comments(self):
        lines = [v["line"] for v in self.found if v["path"] == "src/ui/panel.ts" and v["rule"] == "no-comments"]
        self.assertEqual(lines, [6])
        self.assertFalse(any(v["path"] == "game/core/rules.gd" and v["line"] == 5 for v in self.found))
        self.assertFalse(any(v["path"] == "src/domain/svc.py" and v["line"] in (3, 5) for v in self.found))

    def test_doc_comments_allowed(self):
        self.assertFalse(any(v["path"] == "game/scenes/hud.gd" for v in self.found))
        self.assertFalse(any(v["path"] == "src/ui/panel.ts" and v["line"] == 8 for v in self.found))

    def test_bare_suppression(self):
        self.assertTrue(self.has("src/domain/svc.py", "no-bare-suppression"))
        self.assertTrue(self.has("src/ui/panel.ts", "no-bare-suppression"))

    def test_every_violation_has_fix(self):
        self.assertTrue(all(v["fix"] for v in self.found))

    def test_baseline_ratchet(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = json.loads((FIX / "config.json").read_text())
            cfg["baseline"] = str(Path(d) / "b.json")
            cp = Path(d) / "c.json"
            cp.write_text(json.dumps(cfg))
            code, out = run("--update-baseline", cfg=cp)
            self.assertEqual(code, 0)
            code, found = run(cfg=cp)
            self.assertEqual((code, found), (0, []))
            extra = FIX / "src/ui/extra.ts"
            extra.write_text("setTimeout(() => 1, 1);\n")
            try:
                code, found = run(cfg=cp)
                self.assertEqual(code, 1)
                self.assertEqual({v["path"] for v in found}, {"src/ui/extra.ts"})
            finally:
                extra.unlink()

    def test_dot_directories_are_scanned(self):
        d = FIX / ".hidden"
        d.mkdir(exist_ok=True)
        f = d / "x.ts"
        f.write_text("setTimeout(() => 1, 1);\n")
        try:
            cfg = json.loads((FIX / "config.json").read_text())
            cfg["banned"][0]["globs"] = ["**/*.ts"]
            with tempfile.TemporaryDirectory() as t:
                cp = Path(t) / "c.json"
                cp.write_text(json.dumps(cfg))
                _, found = run(cfg=cp)
            self.assertIn(".hidden/x.ts", {v["path"] for v in found})
        finally:
            f.unlink()
            d.rmdir()

    def test_config_requires_fix(self):
        with tempfile.TemporaryDirectory() as d:
            cp = Path(d) / "c.json"
            cp.write_text(json.dumps({"banned": [{"id": "x", "regex": "y", "message": "m"}]}))
            p = subprocess.run([sys.executable, str(SCRIPT), "--config", str(cp), "--root", str(FIX)], capture_output=True, text=True)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("missing 'fix'", p.stderr)


if __name__ == "__main__":
    unittest.main()
