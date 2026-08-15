#!/usr/bin/env python3
"""Reference smoke test for the Axiom v0.1 artifact protocol.

This is not a replacement for the Rust components. It exists so the packaged
research artifact can exercise the architecture even when Rust is unavailable.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
import tempfile


SPEC = """axiom 0.1
module abs
input x i64
output result i64
domain x -16 16
requires true
ensures result >= 0
ensures result == x || result == -x
objective instructions min
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compile_spec(source: str) -> str:
    values: dict[str, str] = {}
    ensures: list[str] = []
    for raw in source.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line == "axiom 0.1":
            continue
        head, *rest = line.split()
        if head == "module":
            values["module"] = rest[0]
        elif head == "input":
            values["input.name"], values["input.type"] = rest
        elif head == "output":
            values["output.name"], values["output.type"] = rest
        elif head == "domain":
            _, lo, hi = rest
            values["domain.min"] = lo
            values["domain.max"] = hi
        elif head == "requires":
            values["requires.0"] = " ".join(rest)
        elif head == "ensures":
            ensures.append(" ".join(rest))
        elif head == "objective":
            values["objective.metric"], values["objective.direction"] = rest
        else:
            raise ValueError(f"unsupported DSL statement: {line}")
    for index, clause in enumerate(ensures):
        values[f"ensures.{index}"] = clause

    preferred = [
        "module", "input.name", "input.type", "output.name", "output.type",
        "domain.min", "domain.max", "requires.0",
    ]
    lines = ["AXIOM-IR/1"]
    for key in preferred:
        if key in values:
            lines.append(f"{key}={values[key]}")
    for key in sorted(k for k in values if k.startswith("ensures.")):
        lines.append(f"{key}={values[key]}")
    for key in ("objective.metric", "objective.direction"):
        if key in values:
            lines.append(f"{key}={values[key]}")
    return "\n".join(lines) + "\n"


@dataclass(frozen=True)
class Candidate:
    name: str

    def run(self, x: int) -> int:
        if self.name == "x":
            return x
        if self.name == "neg-x":
            return -x
        if self.name == "if-neg":
            return -x if x < 0 else x
        raise ValueError(self.name)

    def program(self) -> str:
        code = {
            "x": ["LOAD_INPUT r0 x", "RETURN r0"],
            "neg-x": ["LOAD_INPUT r0 x", "NEG r1 r0", "RETURN r1"],
            "if-neg": [
                "LOAD_INPUT r0 x",
                "NEG r1 r0",
                "SELECT_NEG r2 r1 r0",
                "RETURN r2",
            ],
        }[self.name]
        return (
            "AXIOM-PROGRAM/1\n"
            "module=abs\n"
            "capabilities=\n"
            f"source_expr={self.name}\n"
            "code:\n"
            + "\n".join(code)
            + "\nend\n"
        )


def valid_result(x: int, result: int) -> bool:
    return result >= 0 and (result == x or result == -x)


def synthesize(lo: int, hi: int) -> Candidate:
    for candidate in map(Candidate, ("x", "neg-x", "if-neg")):
        if all(valid_result(x, candidate.run(x)) for x in range(lo, hi + 1)):
            return candidate
    raise RuntimeError("no candidate")


def verify(ir: str, program: str, candidate: Candidate, lo: int, hi: int) -> str:
    traces = []
    for x in range(lo, hi + 1):
        result = candidate.run(x)
        if not valid_result(x, result):
            raise AssertionError(f"counterexample x={x}, result={result}")
        traces.append(sha256(f"x={x};result={result};ok=true".encode()))
    trace_root = sha256("".join(traces).encode())
    return (
        "AXIOM-PROOF/1\n"
        "kind=bounded-exhaustive\n"
        "module=abs\n"
        f"spec.sha256={sha256(ir.encode())}\n"
        f"program.sha256={sha256(program.encode())}\n"
        f"domain.min={lo}\n"
        f"domain.max={hi}\n"
        f"cases={hi - lo + 1}\n"
        f"trace.merkle={trace_root}\n"
        "verdict=VALID\n"
    )


def proof_gated_execute(ir: str, program: str, receipt: str, candidate: Candidate, x: int) -> int:
    fields = dict(line.split("=", 1) for line in receipt.splitlines()[1:] if "=" in line)
    assert fields["verdict"] == "VALID"
    assert fields["spec.sha256"] == sha256(ir.encode())
    assert fields["program.sha256"] == sha256(program.encode())
    lo, hi = int(fields["domain.min"]), int(fields["domain.max"])
    if not lo <= x <= hi:
        raise ValueError("input outside proven domain")
    return candidate.run(x)


def main() -> None:
    ir = compile_spec(SPEC)
    candidate = synthesize(-16, 16)
    program = candidate.program()
    receipt = verify(ir, program, candidate, -16, 16)
    result = proof_gated_execute(ir, program, receipt, candidate, -13)
    assert result == 13

    # Mutation must invalidate the receipt binding.
    tampered = program.replace("RETURN r2", "RETURN r0")
    try:
        proof_gated_execute(ir, tampered, receipt, candidate, -13)
    except AssertionError:
        tamper_blocked = True
    else:
        tamper_blocked = False
    assert tamper_blocked

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "abs.aix").write_text(ir)
        (out / "abs.axp").write_text(program)
        (out / "abs.axproof").write_text(receipt)

    print("Axiom reference smoke: PASS")
    print(f"synthesized candidate: {candidate.name}")
    print(f"proof-gated run x=-13 -> {result}")
    print("tampered program rejected by receipt binding: yes")


if __name__ == "__main__":
    main()
