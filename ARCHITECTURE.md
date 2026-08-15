# Axiom v0.2 architecture

```text
Axiom 0.2 source
     |
     v
AXIOM-IR/2 ----------------------------+
     |                                  |
     v                                  |
candidate generator                     |
     |                                  |
     v                                  |
AXIOM-PROGRAM/2                         |
     |                                  |
     +--> axiom-symbolic <--------------+
              | VALID / counterexample
              v
       AXIOM-PROOF/2
              |
              v
      verifier receipt gate
              |
              v
          runtime
```

CEGIS makes counterexamples first-class artifacts. The long-term TCB is intended to shrink toward a small proof checker
plus formally connected execution semantics.
