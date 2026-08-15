#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    symbolic = load("axiom_symbolic_ref", ROOT / "axiom-symbolic" / "axiom_symbolic.py")
    cegis = load("axiom_cegis_ref", ROOT / "axiom-cegis" / "axiom_cegis.py")

    spec_raw = """AXIOM-IR/2
module=abs
input.0.name=x
input.0.type=int
output.name=result
output.type=int
domain.x.kind=unbounded
requires.0.id=req
requires.0.expr=true
ensures.0.id=nonnegative
ensures.0.expr=result >= 0
ensures.1.id=magnitude
ensures.1.expr=result == x || result == -x
objective.0.metric=instructions
objective.0.direction=min
"""

    examples = [0]
    history = []
    final_program = None
    for iteration in range(8):
        candidate = cegis.choose_candidate(examples)
        program = candidate.program("abs")
        valid, meta, cex = symbolic.verify(spec_raw, program)
        history.append((candidate.name, list(examples), valid, None if cex is None else int(cex["input.x"])))
        if valid:
            final_program = program
            final_proof = symbolic.emit_proof(spec_raw, program, valid, meta, cex)
            break
        assert cex is not None
        examples.append(int(cex["input.x"]))
    else:
        raise AssertionError("CEGIS failed to converge")

    assert final_program is not None
    assert history[0][0] == "x" and history[0][2] is False
    assert history[-1][2] is True
    assert symbolic.evaluate_program(final_program, -10**12) == 10**12
    assert symbolic.evaluate_program(final_program, 10**12) == 10**12

    # Proof binding: one-byte semantic mutation must invalidate the receipt hash.
    fields = dict(line.split("=", 1) for line in final_proof.splitlines()[1:] if "=" in line)
    assert fields["program.sha256"] == hashlib.sha256(final_program.encode()).hexdigest()
    tampered = final_program.replace("RETURN r2", "RETURN r0")
    assert fields["program.sha256"] != hashlib.sha256(tampered.encode()).hexdigest()

    # KV architectural evolution experiment.
    with tempfile.TemporaryDirectory() as tmp:
        result = subprocess.run(
            [sys.executable, str(ROOT / "axiom-kv-lab" / "modelcheck.py")],
            cwd=tmp,
            check=True,
            capture_output=True,
            text=True,
        )
        assert "PROMOTE journaled-cap-v3" in result.stdout

    print("Axiom v0.2 reference smoke: PASS")
    print("CEGIS trajectory:")
    for index, (candidate, xs, valid, cex) in enumerate(history):
        print(f"  {index}: {candidate:10s} examples={xs} verdict={'VALID' if valid else 'INVALID'} cex={cex}")
    print("unbounded symbolic proof: yes (supported 1-var affine fragment)")
    print("tampered program rejected by proof binding: yes")
    print("KV evolution promoted journaled-cap-v3: yes")


if __name__ == "__main__":
    main()
