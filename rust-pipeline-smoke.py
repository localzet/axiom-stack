#!/usr/bin/env python3
"""Exercise the Rust compiler, receipt gate and VM against the symbolic backend."""
from __future__ import annotations

import argparse
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent


def load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser(description="Проверить Rust pipeline Axiom")
    parser.add_argument("--bin-dir", type=Path, required=True)
    args = parser.parse_args()
    binaries = args.bin_dir.resolve()
    suffix = ".exe" if os.name == "nt" else ""
    symbolic = load("pipeline_symbolic", ROOT / "axiom-symbolic" / "axiom_symbolic.py")
    cegis = load("pipeline_cegis", ROOT / "axiom-cegis" / "axiom_cegis.py")

    def run(name: str, *arguments: str, accepted: bool = True) -> str:
        result = subprocess.run(
            [str(binaries / (name + suffix)), *arguments],
            capture_output=True,
            text=True,
        )
        if accepted != (result.returncode == 0):
            raise AssertionError(
                f"{name}: unexpected exit {result.returncode}: {result.stderr}"
            )
        return result.stdout.strip()

    with tempfile.TemporaryDirectory(prefix="axiom-pipeline-") as directory:
        temp = Path(directory)
        source, spec, program, proof = [
            temp / name
            for name in ("abs.ax", "abs.aix", "abs.axp", "abs.axproof")
        ]
        source.write_text("""axiom 0.2
module abs
input x int
output result int
domain x unbounded
requires true
ensures nonnegative: result >= 0
ensures magnitude: result == x || result == -x
objective instructions min
""", encoding="utf-8", newline="\n")
        run("axiom-spec", "compile", str(source), "--out", str(spec))
        raw_spec = spec.read_text(encoding="utf-8")
        raw_program = cegis.Candidate("abs-branch", 4).program("abs")
        valid, metadata, counterexample = symbolic.verify(raw_spec, raw_program)
        if not valid or counterexample is not None:
            raise AssertionError("Symbolic backend rejected the abs fixture")
        raw_proof = symbolic.emit_proof(raw_spec, raw_program, valid, metadata, counterexample)
        program.write_text(raw_program, encoding="utf-8", newline="\n")
        proof.write_text(raw_proof, encoding="utf-8", newline="\n")
        verify_args = (str(spec), str(program), str(proof))
        run("axiom-verifier", "check-receipt", *verify_args)

        def execute(value: int, accepted: bool = True) -> str:
            return run(
                "axiom-runtime", "run", "--spec", str(spec),
                "--program", str(program), "--proof", str(proof),
                "--x", str(value), accepted=accepted,
            )

        for value in (-(2**63) + 1, -123, -1, 0, 1, 123, 2**63 - 1):
            if execute(value) != str(abs(value)):
                raise AssertionError(f"VM result differs from abs({value})")
        execute(-(2**63), accepted=False)

        program.write_text(
            raw_program.replace("RETURN r2", "RETURN r0"),
            encoding="utf-8",
            newline="\n",
        )
        run("axiom-verifier", "check-receipt", *verify_args, accepted=False)
        execute(-123, accepted=False)
        program.write_text(raw_program, encoding="utf-8", newline="\n")
        for changed in (
            raw_proof.replace("verdict=VALID", "verdict=INVALID"),
            raw_proof.replace("exact-for-supported-fragment", "finite-examples-only"),
            raw_proof + "verdict=VALID\n",
        ):
            proof.write_text(changed, encoding="utf-8", newline="\n")
            run("axiom-verifier", "check-receipt", *verify_args, accepted=False)
            execute(-123, accepted=False)
    print("Rust pipeline: PASS (compiler, symbolic receipt, verifier, VM, i64 limits and artifact rejection)")


if __name__ == "__main__":
    main()
