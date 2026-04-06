# artifact_metadata_spec.md

## 0. Scope

This file defines the **artifact metadata contract** for the validation system.

It is a **build-time specification**, not documentation.

It standardizes:
- artifact identity
- traceability requirements
- reproducibility guarantees
- dependency boundaries

---

## 1. Core Principle

> Every artifact MUST be identifiable, reproducible, and traceable.

No artifact is valid without complete metadata.

---

## 2. Artifact Coverage

This spec applies to all pipeline artifacts:

- CanonicalResult
- MetricsBundle
- ValidationReport
- (optional) intermediate outputs

It aligns with:
- canonical_result.md fileciteturn0file0
- metrics_design.md fileciteturn0file1
- statistical_validation.md fileciteturn0file3
- architecture_v2.md fileciteturn0file4

---

## 3. Global Metadata Schema (MANDATORY)

All artifacts MUST include:

```python
ArtifactMeta = {
    "artifact_type": str,
    "artifact_version": str,

    "run_id": str,
    "config_id": str,
    "config_version": str,
    "engine_version": str,

    "schema_version": str,

    "rng_seed": int | None,

    "generated_at": str
}
```

---

## 4. Field Constraints

### 4.1 Identity

- artifact_type MUST be explicit
- artifact_version MUST follow semantic versioning
- run_id MUST match CanonicalResult.run.run_id

---

### 4.2 Reproducibility

The following MUST be sufficient to replay:

```
(config_id, config_version, engine_version, rng_seed)
```

Rules:

- rng_seed MUST be present for all engine-generated artifacts
- MUST NOT rely on external state

---

### 4.3 Time

- generated_at MUST be ISO8601 UTC
- MUST NOT use local time

---

### 4.4 Schema Control

- schema_version MUST be explicit
- breaking changes MUST increment version

---

## 5. Artifact-Specific Requirements

### 5.1 CanonicalResult

- MUST contain full RunMeta (see canonical_result.md)
- metadata MUST NOT be duplicated inconsistently
- MUST be replayable

---

### 5.2 MetricsBundle

- meta MUST align with CanonicalResult
- MUST NOT introduce new identifiers
- MUST NOT override upstream metadata

---

### 5.3 ValidationReport

- MUST reference run_id + config_id
- MUST include validation_version
- MUST be derivable from MetricsBundle + rules

---

## 6. Dependency Consistency

Pipeline:

config → engine → canonical → metrics → validation

Rules:

- downstream artifacts MUST inherit upstream identity
- no artifact may redefine run context
- no reverse dependency allowed

---

## 7. Traceability Rules

Every artifact MUST allow:

- trace to config
- trace to RNG seed
- trace to engine version
- trace to upstream artifact

---

## 8. Forbidden Patterns

- missing run_id
- implicit seed
- inconsistent config references
- runtime-modified metadata
- mixing multiple runs in one artifact

---

## 9. Minimal Interface Contract

All generators MUST attach metadata:

```python
generate_xxx(...) -> {
    "meta": ArtifactMeta,
    "data": ...
}
```

---

## 10. Validation Checklist

Before accepting any artifact:

- [ ] metadata complete
- [ ] run_id consistent
- [ ] seed present if required
- [ ] version fields valid
- [ ] reproducible inputs defined

---

## Summary

Artifact metadata ensures:

- reproducibility
- auditability
- pipeline consistency

It is the **identity layer of the system**, not business logic.
