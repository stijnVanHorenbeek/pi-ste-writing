# pi-ste-writing

Semantic-safe technical writing skill for [Pi](https://pi.dev).

> [!NOTE]
> V1 is under development. Package is private until release review is complete.

## Scope

Package will provide one progressively loaded skill, `clear-technical-writing`, with three modes:

- **Clear:** concise technical prose without strict STE limits.
- **Procedure:** action-oriented instructions with ordered conditions and warnings.
- **Strict STE:** explicit, compliance-oriented checks with semantic safeguards.

Technical correctness and source fidelity take priority over style. Package does not auto-load extensions, prompt templates, themes, or global instructions.

See [`docs/v1-acceptance-contract.md`](docs/v1-acceptance-contract.md) for V1 scope and completion gates.

## Package layout

```text
skills/clear-technical-writing/  Pi skill and on-demand resources
tests/                           deterministic tests and regression fixtures
evals/                           reproducible Pi evaluation tooling
```

Installation and usage instructions will be added after native Pi discovery is validated.

## Upstream and attribution

This project adapts [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) at commit [`59bf670`](https://github.com/AminBlg/SimpleEnglish/commit/59bf6702197a5aadc96d197ea17f290d8d50dcd3), licensed under the MIT License.

ASD-STE100 is a registered trademark of ASD. This project is not affiliated with ASD, STEMG, or AminBlg. It does not include the official ASD-STE100 dictionary and cannot certify ASD-STE100 compliance.

## License

MIT. See [`LICENSE`](LICENSE).
