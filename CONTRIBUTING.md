# Contributing to Project Varsha

Thank you for contributing to Project Varsha. We maintain rigorous standards for meteorological correctness, data leakage prevention, test coverage, and design integrity.

---

## 1. Non-Negotiable Development Rules

1. **Honest Provenance (N1):** Distinguish between `synthetic` and `real` data modes at all times. Never present synthetic scores as real atmospheric skill.
2. **Leakage Prevention (N4):** All new features must be registered in `src/varsha/features/registry.py` with valid availability timestamps.
3. **Evidence Over Claims:** Commit code only with corresponding test execution logs.
4. **No Gaming (N5):** Never modify or weaken a test threshold without an approved ADR.
5. **Anti-Template Design (N9):** UI contributions must pass the AI-look audit (Appendix B).

---

## 2. Local Development Workflow

```bash
# 1. Install dependencies
make setup

# 2. Run fast CI verification
make demo-fast

# 3. Run full verification before pushing
make verify
```
