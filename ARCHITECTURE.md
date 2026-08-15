# Axiom architecture v0.1

```text
human intent (.ax)
      |
      v
 axiom-spec --------> AXIOM-IR/1 (.aix)
                          |
              +-----------+-----------+
              |                       |
              v                       v
        axiom-synth              axiom-solver
        (untrusted)               (backend)
              |
              v
      AXIOM-PROGRAM/1 (.axp)
              |
              v
       axiom-verifier
              |
              v
       AXIOM-PROOF/1 (.axproof) -----> axiom-proof DAG
              |
              v
        axiom-runtime ---- execution commitment ---> axiom-zk-bridge
```

## Central invariant

`runtime_accepts(program) => exists receipt . verifier_accepts(spec, program, receipt)`

v0.1 enforces the implication by SHA-256 binding of the exact spec and program bytes in the proof receipt.
