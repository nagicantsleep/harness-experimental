#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

LANGS = {
    ".ts": "c", ".tsx": "c", ".js": "c", ".jsx": "c", ".mjs": "c", ".cjs": "c",
    ".cs": "c", ".java": "c", ".kt": "c", ".go": "c", ".rs": "c", ".swift": "c",
    ".c": "c", ".cpp": "c", ".h": "c", ".hpp": "c", ".dart": "c",
    ".py": "py", ".gd": "gd", ".rb": "rb", ".sh": "rb", ".yml": "rb", ".yaml": "rb",
}

IMPORT_RES = {
    ".ts": [r"""(?:import|export)\s[^'"]*?from\s+['"]([^'"]+)['"]""", r"""import\s+['"]([^'"]+)['"]""", r"""import\(\s*['"]([^'"]+)['"]\s*\)""", r"""require\(\s*['"]([^'"]+)['"]\s*\)"""],
    ".py": [r"^\s*from\s+([\w.]+)\s+import\s", r"^\s*import\s+([\w.]+)"],
    ".cs": [r"^\s*(?:global\s+)?using\s+(?:static\s+)?([\w.]+)\s*;"],
    ".gd": [r"""(?:preload|load)\(\s*['"]([^'"]+)['"]\s*\)""", r"""^\s*extends\s+['"]([^'"]+)['"]"""],
    ".go": [r"""^\s*(?:import\s+)?(?:\w+\s+)?"([\w./-]+)"\s*$"""],
    ".rs": [r"^\s*(?:pub\s+)?use\s+([\w:]+)"],
    ".java": [r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;"],
    ".kt": [r"^\s*import\s+([\w.]+)"],
    ".swift": [r"^\s*import\s+(\w+)"],
}
for _e in (".tsx", ".js", ".jsx", ".mjs", ".cjs"):
    IMPORT_RES[_e] = IMPORT_RES[".ts"]

TRIPLE = ('"""', "'''")


@dataclass
class Violation:
    rule: str
    path: str
    line: int
    message: str
    fix: str


def load_config(path):
    cfg = json.loads(Path(path).read_text())
    for rule in cfg.get("banned", []):
        for key in ("id", "regex", "message", "fix"):
            if not rule.get(key):
                sys.exit(f"config error: banned rule {rule.get('id', '?')} is missing '{key}'. Every rule must say how to fix the violation.")
    for layer in cfg.get("layers", []):
        if not layer.get("fix"):
            sys.exit(f"config error: layer {layer.get('name', '?')} is missing 'fix'.")
    return cfg


def iter_files(root, cfg):
    skip = cfg.get("exclude", [])
    for base, dirs, files in os.walk(root):
        rel_base = os.path.relpath(base, root).replace(os.sep, "/")
        prefix = "" if rel_base == "." else rel_base + "/"
        dirs[:] = [d for d in dirs if d != ".git" and not matches(prefix + d, skip + ["**/node_modules", "**/__pycache__"])]
        for name in files:
            rel = prefix + name
            if Path(name).suffix in LANGS and not matches(rel, skip):
                yield rel


def matches(rel, globs):
    return any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(rel, g.rstrip("/") + "/*") for g in globs)


def in_scope(rel, globs):
    return not globs or matches(rel, globs)


def scan_comments(text, ext):
    kind = LANGS[ext]
    if kind == "c":
        line_m, block = ["//"], ("/*", "*/")
        quotes = ['"', "'", "`"] if ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".go", ".dart") else ['"']
    elif kind == "py":
        line_m, block, quotes = ["#"], None, ['"', "'"]
    elif kind == "gd":
        line_m, block, quotes = ["#"], None, ['"', "'"]
    else:
        line_m, block, quotes = ["#"], None, ['"', "'"]
    out = []
    i, n, line = 0, len(text), 1
    code_on_line = False
    while i < n:
        ch = text[i]
        if ch == "\n":
            line += 1
            code_on_line = False
            i += 1
            continue
        if kind in ("py", "gd") and text.startswith(TRIPLE, i):
            q = text[i:i + 3]
            j = text.find(q, i + 3)
            j = n if j < 0 else j + 3
            line += text.count("\n", i, j)
            i, code_on_line = j, True
            continue
        if ch in quotes and not (kind == "c" and ch == "'" and ext in (".rs",)):
            j = i + 1
            while j < n and text[j] != ch and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            i, code_on_line = j + 1, True
            continue
        if any(text.startswith(m, i) for m in line_m):
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append((line, text[i:j], code_on_line))
            i = j
            continue
        if block and text.startswith(block[0], i):
            j = text.find(block[1], i + 2)
            j = n if j < 0 else j + 2
            out.append((line, text[i:j], code_on_line))
            line += text.count("\n", i, j)
            i, code_on_line = j, True
            continue
        if not ch.isspace():
            code_on_line = True
        i += 1
    return out


def comment_allowed(body, line, cfg_c, head):
    for pat in cfg_c.get("allow_regex", []):
        if re.search(pat, body):
            return True
    if line <= cfg_c.get("license_header_lines", 15) and re.search(r"(?i)copyright|license|spdx", head):
        return True
    return False


def check_comments(rel, text, ext, cfg_c, found):
    if not cfg_c or ext not in LANGS or not in_scope(rel, cfg_c.get("globs", [])):
        return
    mode = cfg_c.get("mode", "justify-only")
    sus = re.compile(cfg_c.get("justifying_regex", r"(?i)\b(hack|workaround|temporary|temp fix|for now|fine for now|do not remove|don't remove|too risky|because \w+ (said|asked|told)|legacy reasons|quick fix)\b"))
    fix_text = cfg_c.get("fix", "Delete the comment. If the code needs explaining, rename the symbol, extract a function, or encode the invariant in a type. If the code is a workaround, fix the root cause instead of documenting it.")
    for line, body, trailing in scan_comments(text, ext):
        if sus.search(body):
            found.append(Violation("no-justifying-comments", rel, line, f"Comment justifies a workaround: {body.strip()[:80]}", fix_text))
            continue
        if mode == "strict" and not comment_allowed(body, line, cfg_c, text[:600]):
            found.append(Violation("no-comments", rel, line, f"Comment is not on the allow-list: {body.strip()[:80]}", fix_text))


def check_suppressions(rel, text, cfg_s, found):
    if not cfg_s or not in_scope(rel, cfg_s.get("globs", [])):
        return
    pat = re.compile(cfg_s["regex"])
    ok = re.compile(cfg_s.get("allowed_if", r"(?:https?://\S+|\b[A-Z][A-Z0-9]+-\d+\b|#\d+)"))
    for no, raw in enumerate(text.splitlines(), 1):
        if pat.search(raw) and not ok.search(raw):
            found.append(Violation("no-bare-suppression", rel, no, "Lint or type suppression without a ticket or link.", cfg_s.get("fix", "Remove the suppression and fix the underlying finding. If the rule is wrong, change the rule config in a reviewed PR; if it cannot be fixed now, add a ticket id on the same line.")))


def check_banned(rel, text, cfg, found):
    for rule in cfg.get("banned", []):
        if not in_scope(rel, rule.get("globs", [])) or matches(rel, rule.get("except", [])):
            continue
        pat = re.compile(rule["regex"])
        for no, raw in enumerate(text.splitlines(), 1):
            if pat.search(raw):
                found.append(Violation(rule["id"], rel, no, rule["message"], rule["fix"]))


def resolve_import(spec, rel, ext, cfg):
    if ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        for alias, target in cfg.get("aliases", {}).items():
            if spec.startswith(alias):
                return ("path", os.path.normpath(target + spec[len(alias):]).replace(os.sep, "/"))
        if spec.startswith("."):
            return ("path", os.path.normpath(os.path.join(os.path.dirname(rel), spec)).replace(os.sep, "/"))
        return ("module", spec)
    if ext == ".gd":
        if spec.startswith("res://"):
            return ("path", spec[6:])
        return ("path", os.path.normpath(os.path.join(os.path.dirname(rel), spec)).replace(os.sep, "/"))
    return ("module", spec)


def layer_of(kind, target, layers):
    for layer in layers:
        if kind == "path" and any(target == p.rstrip("/") or target.startswith(p.rstrip("/") + "/") for p in layer.get("paths", [])):
            return layer["name"]
        if any(target == ns or target.startswith(ns + ".") or target.startswith(ns + "/") or target.startswith(ns + "::") for ns in layer.get("namespaces", [])):
            return layer["name"]
    return None


def check_layers(rel, text, ext, cfg, found):
    layers = cfg.get("layers", [])
    if not layers or ext not in IMPORT_RES:
        return
    mine = next((l for l in layers if any(rel.startswith(p.rstrip("/") + "/") for p in l.get("paths", []))), None)
    if mine is None:
        return
    forbidden = set(mine.get("must_not_import", []))
    allowed = mine.get("may_import")
    for no, raw in enumerate(text.splitlines(), 1):
        for pattern in IMPORT_RES[ext]:
            m = re.search(pattern, raw)
            if not m:
                continue
            kind, target = resolve_import(m.group(1), rel, ext, cfg)
            dest = layer_of(kind, target, layers)
            if dest is None or dest == mine["name"]:
                continue
            bad = dest in forbidden or (allowed is not None and dest not in allowed)
            if bad:
                found.append(Violation(f"layer-{mine['name']}-must-not-import-{dest}", rel, no, f"Layer '{mine['name']}' imports layer '{dest}' ({m.group(1)}).", mine["fix"]))
            break


def run(root, cfg):
    found = []
    for rel in sorted(iter_files(root, cfg)):
        ext = Path(rel).suffix
        text = (Path(root) / rel).read_text(errors="replace")
        check_layers(rel, text, ext, cfg, found)
        check_banned(rel, text, cfg, found)
        check_suppressions(rel, text, cfg.get("suppressions"), found)
        check_comments(rel, text, ext, cfg.get("comments"), found)
    return found


def apply_baseline(found, baseline_path):
    if not baseline_path or not Path(baseline_path).exists():
        return found
    base = json.loads(Path(baseline_path).read_text())
    seen = Counter()
    fresh = []
    for v in found:
        key = f"{v.rule}::{v.path}"
        seen[key] += 1
        if seen[key] > base.get(key, 0):
            fresh.append(v)
    return fresh


def main():
    ap = argparse.ArgumentParser(description="Language-agnostic architecture and slop gate.")
    ap.add_argument(
        "--config",
        default="harness.config.json",
        help="Path to harness.config.json (layers, banned, comments, suppressions, baseline).",
    )
    ap.add_argument("--root", default=".")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    cfg = load_config(args.config)
    found = run(args.root, cfg)
    baseline_path = cfg.get("baseline")
    if args.update_baseline:
        counts = Counter(f"{v.rule}::{v.path}" for v in found)
        Path(baseline_path).parent.mkdir(parents=True, exist_ok=True)
        Path(baseline_path).write_text(json.dumps(dict(sorted(counts.items())), indent=1) + "\n")
        print(f"baseline written: {len(found)} existing violations frozen in {baseline_path}")
        return 0
    found = apply_baseline(found, baseline_path)
    if args.json:
        print(json.dumps([v.__dict__ for v in found], indent=1))
    else:
        for v in found:
            print(f"{v.path}:{v.line}  [{v.rule}]  {v.message}\n    FIX: {v.fix}")
        print(f"\n{len(found)} violation(s)")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
