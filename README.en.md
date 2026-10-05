# axiom-stack v0.2.0

Meta-repository and reproducible reference pipeline for **Autopoietic Proof-Carrying Computing**.

## v0.2 breakthrough

The bundled reference path no longer proves `abs` by enumerating a finite domain. `axiom-cegis` obtains counterexamples
from `axiom-symbolic` until it synthesizes a program that is symbolically valid for **all mathematical integers in the
supported one-variable affine fragment**.

Run from this repository after all sibling repositories are present:

```bash
python reference-v0.2.py
```

The script also checks proof-binding tamper rejection and runs the KV architectural evolution experiment.

## Attribution

Maintainer of Localzet contributions: **Ivan Zorin (localzet)** — <creator@localzet.com> · https://www.localzet.com. Copyright © 2026 Localzet Group. Original authorship and third-party licenses remain applicable. See [AUTHORS](.github/AUTHORS.md).
