#!/usr/bin/env python3
"""
check-exam-zh-symbols.py

Scan .tex files for exam-zh overridden math symbols that are NOT using
the star (*) variant (which reverts to the original LaTeX symbol).

Usage:
    python check-exam-zh-symbols.py                    # scan current dir
    python check-exam-zh-symbols.py [DIR]             # scan a specific dir
    python check-exam-zh-symbols.py -f SYMBOLS_FILE   # custom symbol list

Exit code: 0 = clean, 1 = violations found
"""

import argparse
import os
import re
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SYMBOLS_FILE = os.path.join(SCRIPT_DIR, "overriden-symbols.txt")

# Fallback: only used when NOT inside a git repo
FALLBACK_SKIP_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "_build",
    "out",
}

_COMMENT_RE = re.compile(r"%.*?$", re.MULTILINE)


def load_symbols(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        symbols = [line.strip() for line in f if line.strip() and not line.lstrip().startswith("#")]
    symbols.sort(key=len, reverse=True)
    return symbols


def strip_latex_comment(line: str) -> str:
    """Remove LaTeX comments (mirrors bib_lookup.utils._remove_comments)."""
    return _COMMENT_RE.sub("", line)


def build_pattern(symbols: list[str]) -> re.Pattern:
    alt = "|".join(re.escape(s) for s in symbols)
    return re.compile(r"\\(" + alt + r")(?![a-zA-Z*])")


# ── File discovery ──────────────────────────────────────────────────────


def _git_ls_tex(directory: str) -> list[str] | None:
    """Use git ls-files to get .tex paths. Returns None if not in a git repo."""
    try:
        result = subprocess.run(
            ["git", "-C", directory, "ls-files", "--cached", "--others", "--exclude-standard", "*.tex"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [os.path.join(directory, line.strip()) for line in result.stdout.splitlines() if line.strip()]
        return files if files else None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _walk_tex_files(directory: str) -> list[str]:
    """Fallback: walk the filesystem when not inside a git repo."""
    files = []
    for root, dirs, fnames in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d not in FALLBACK_SKIP_DIRS and not d.startswith("."))
        for fname in sorted(fnames):
            if fname.endswith(".tex"):
                files.append(os.path.join(root, fname))
    return files


def get_tex_files(directory: str) -> list[str]:
    """Return .tex file paths, preferring git to respect .gitignore."""
    git_files = _git_ls_tex(directory)
    if git_files is not None:
        return git_files
    print(
        "Warning: not in a git repo, falling back to filesystem walk " "(.gitignore not respected)",
        file=sys.stderr,
    )
    return _walk_tex_files(directory)


# ── Scanning ────────────────────────────────────────────────────────────


def find_violations(files: list[str], pattern: re.Pattern):
    for fpath in files:
        try:
            with open(fpath, encoding="utf-8") as f:
                lines = f.readlines()
        except (OSError, UnicodeDecodeError) as exc:
            print(f"Warning: Cannot read {fpath}: {exc}", file=sys.stderr)
            continue
        for lineno, raw_line in enumerate(lines, 1):
            code = strip_latex_comment(raw_line)
            for m in pattern.finditer(code):
                yield fpath, lineno, m.group(), code.rstrip()


# ── ANSI helpers ────────────────────────────────────────────────────────

_USE_COLOR = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    if _USE_COLOR:
        return f"\033[{code}m{text}\033[0m"
    return text


RED, GREEN, CYAN, BOLD = "1;31", "1;32", "0;36", "1"


# ── Main ────────────────────────────────────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser(description="Check .tex files for non-star usages of exam-zh overridden symbols.")
    ap.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Root directory to scan (default: current directory)",
    )
    ap.add_argument(
        "-f",
        "--symbols-file",
        default=DEFAULT_SYMBOLS_FILE,
        help=f"Path to the symbol list file (default: {DEFAULT_SYMBOLS_FILE})",
    )
    ap.add_argument("--no-color", action="store_true", help="Disable coloured output")
    args = ap.parse_args()

    global _USE_COLOR
    if args.no_color:
        _USE_COLOR = False

    symbols_file = os.path.abspath(args.symbols_file)
    if not os.path.isfile(symbols_file):
        print(f"Error: Symbol list not found: {symbols_file}", file=sys.stderr)
        return 2

    symbols = load_symbols(symbols_file)
    pattern = build_pattern(symbols)
    tex_files = get_tex_files(args.directory)
    violations = list(find_violations(tex_files, pattern))

    if violations:
        seen: set[str] = set()
        for fpath, lineno, cmd, line_content in violations:
            rel = os.path.relpath(fpath)
            if rel not in seen:
                print(f"\n{_c(BOLD, rel)}")
                seen.add(rel)
            print(f"  {_c(RED, f'L{lineno:4d}')}  {cmd}  | {line_content}")
        hint = r"\command*"
        print(
            f"\n{_c(RED, f'Found {len(violations)} violation(s) in {len(seen)} file(s).')}\n"
            f"    Use {_c(CYAN, hint)} to get the original LaTeX symbol.\n"
        )
        return 1
    else:
        print(_c(GREEN, "No exam-zh overridden symbols found without '*'."))
        return 0


if __name__ == "__main__":
    sys.exit(main())
