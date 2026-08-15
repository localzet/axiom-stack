# axiom-stack

Meta-repository for the Axiom Autopoietic Proof-Carrying Computing research stack.

## Repositories

- `axiom-spec` - intent DSL -> canonical IR
- `axiom-ir` - IR validation/canonical hashing
- `axiom-solver` - finite-domain logic backend + SMT-LIB bridge
- `axiom-synth` - untrusted enumerative synthesizer
- `axiom-verifier` - independent bounded verifier + receipt
- `axiom-runtime` - proof-gated VM
- `axiom-capabilities` - no-ambient-authority capability model
- `axiom-proof` - append-only proof DAG seed
- `axiom-zk-bridge` - external zkVM proof envelope
- `axiom-node` - process-level orchestration
- `axiom-kv-lab` - self-evolving crash-safe KV experiment
- `axiom-research` - papers, formal model and research roadmap

## Local integration

Build each Rust repo and copy its executable into one directory, then point `axiom-node` at it. The repositories
communicate through versioned artifacts rather than Rust-internal APIs.

## Trust model

Axiom intentionally distinguishes four roles:

1. **specification author** - chooses what must hold;
2. **proposer/synthesizer** - may be buggy or adversarial;
3. **verifier** - checks a candidate against the formalized contract;
4. **runtime** - executes only artifacts bound to an accepted receipt.

The v0.1 verifier is bounded. The research roadmap replaces/augments it with SMT, proof assistants and proof-producing
backends while retaining the same authority separation.
