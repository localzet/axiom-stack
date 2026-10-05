#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Ivan Zorin <creator@localzet.com> (Localzet contributions)
# SPDX-License-Identifier: MIT
"""Fetch the pinned research components without overwriting local work."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess


def git(directory: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(directory), *args], text=True).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Загрузить зафиксированные компоненты Axiom")
    parser.add_argument("--directory", type=Path, required=True)
    args = parser.parse_args()
    destination = args.directory.resolve()
    destination.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(Path(__file__).with_name("components.json").read_text())
    for component in manifest["components"]:
        target = destination / component["name"]
        revision = component["revision"]
        if target.exists():
            if not (target / ".git").is_dir() or git(target, "rev-parse", "HEAD") != revision:
                raise SystemExit(f"Несовпадение версии в {target}; локальные файлы не изменены")
            if git(target, "status", "--porcelain"):
                raise SystemExit(f"Незакоммиченные изменения в {target}; локальные файлы не изменены")
            continue
        subprocess.run(["git", "clone", "--no-checkout", component["url"], str(target)], check=True)
        subprocess.run(["git", "-C", str(target), "checkout", "--detach", revision], check=True)
    print(f"Компоненты Axiom загружены в {destination}")


if __name__ == "__main__":
    main()
