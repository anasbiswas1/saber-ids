"""Single commit step for this repo. Run from the scratch console notebook only:

    subprocess.run(["python", "tools/commit_cell.py", "message"])

Restores git identity and credentials from the Drive project folder, strips all notebook outputs,
refuses to commit credential files or files containing a secret token pattern, leaves model
checkpoints, raw data and oversized files unstaged, commits if anything is staged, and always
pushes the current branch so unpushed commits never remain local.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from glob import glob
from pathlib import Path

DRIVE_PROJECT_ROOT = Path("/content/drive/MyDrive/SABER_Research")
REPO_ROOT = Path(os.environ.get("SABER_REPO_ROOT", str(DRIVE_PROJECT_ROOT / "saber-ids")))
GIT_NAME = "Md Anas Biswas"
GIT_EMAIL = "anasbiswas@gmail.com"
FORBIDDEN_NAMES = {".git-credentials", ".gitconfig", "kaggle.json", ".env"}
FORBIDDEN_PREFIXES = (".secrets/",)
SKIP_PREFIXES = ("data/",)
SKIP_SUFFIXES = (".pt", ".pth", ".ckpt", ".parquet", ".npy", ".npz", ".pkl")
MAX_FILE_MB = 50
SECRET_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"sk-[A-Za-z0-9]{32,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_\-]{35}"),
]
TEXT_EXT = {".py", ".ipynb", ".md", ".txt", ".json", ".csv", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".sh"}


def run(args, check=True):
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"{' '.join(args)}\n{r.stdout}{r.stderr}")
    return r.stdout


def strip_outputs():
    import nbformat
    notebooks = sorted(glob(str(REPO_ROOT / "notebooks" / "*.ipynb")))
    for notebook in notebooks:
        nb = nbformat.read(notebook, as_version=4)
        changed = False
        for cell in nb.cells:
            if cell.cell_type == "code" and (cell.get("outputs") or cell.get("execution_count") is not None):
                cell["outputs"] = []
                cell["execution_count"] = None
                changed = True
        if "widgets" in nb.metadata:
            del nb.metadata["widgets"]
            changed = True
        if changed:
            nbformat.write(nb, notebook)
    print(f"outputs: checked {len(notebooks)} notebook(s)")


def secret_scan(paths):
    hits = []
    for p in paths:
        path = REPO_ROOT / p
        if path.suffix.lower() not in TEXT_EXT or not path.is_file():
            continue
        try:
            txt = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(txt):
                hits.append(f"{p} ({pat.pattern[:14]}...)")
                break
    return hits


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        raise SystemExit('usage: python tools/commit_cell.py "commit message"')
    message = sys.argv[1].strip()

    for dotfile in (".gitconfig", ".git-credentials"):
        source = DRIVE_PROJECT_ROOT / dotfile
        if source.exists():
            shutil.copy(source, Path.home() / dotfile)
    credentials = Path.home() / ".git-credentials"
    if credentials.exists():
        os.chmod(credentials, 0o600)

    os.chdir(REPO_ROOT)
    run(["git", "config", "user.name", GIT_NAME])
    run(["git", "config", "user.email", GIT_EMAIL])
    run(["git", "config", "credential.helper", "store"])

    strip_outputs()

    run(["git", "add", "-A"])
    staged = [l for l in run(["git", "diff", "--cached", "--name-only"]).splitlines() if l.strip()]
    skip = [p for p in staged if p.startswith(SKIP_PREFIXES) or p.lower().endswith(SKIP_SUFFIXES)
            or (Path(p).exists() and Path(p).stat().st_size > MAX_FILE_MB * 1024 * 1024)]
    if skip:
        run(["git", "reset", "-q", "--"] + skip, check=False)
        print(f"left unstaged ({len(skip)} checkpoint, data or oversized file(s)): {skip[:10]}{' ...' if len(skip) > 10 else ''}")
        staged = [p for p in staged if p not in set(skip)]
    bad = [p for p in staged if Path(p).name in FORBIDDEN_NAMES or p.startswith(FORBIDDEN_PREFIXES)]
    secrets = secret_scan(staged)
    if bad or secrets:
        run(["git", "reset", "-q"], check=False)
        raise SystemExit(f"refused: forbidden={bad} secrets_in={secrets}")

    if staged:
        commit = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
        print(commit.stdout or commit.stderr)
    else:
        print("nothing new to commit; pushing any unpushed commits")

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    push = subprocess.run(["git", "push", "origin", branch], capture_output=True, text=True)
    print(push.stdout or push.stderr)
    print(run(["git", "log", "--oneline", "-1"]).strip())
    print(run(["git", "status", "--short"]).strip() or "working tree clean")


if __name__ == "__main__":
    main()
