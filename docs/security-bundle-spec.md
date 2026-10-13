# Security Bundle — Phase 2 spec: Build · Probe · Receipt

Status: **spec, not implemented.** Branch `spec/security-bundle`, stacked on
`feat/secure-apply` (PR #11, unmerged). Date: 2026-10-13.

Goal: reusable code with reproducible security evidence attached. A security
block ships with its own threat model and probes; Block-Wise generates the block
behind Secure Apply, runs the probes against the generated code locally, and
returns a receipt that records what was tested, what held, and what was not
tested.

Frozen scope: no live network scanning, no web scanner, no outbound HTTP from
probes, no merges. Everything runs locally in a temp directory.

---

## 1. Review findings

### 1.1 Secure Apply (PR #11): holds

- `secure_apply()` enforces identity (canonical SHA-256 vs `approved.json`),
  workspace containment (`resolve()` + parents check), and fail-closed
  verification (≥1 function checked, no issues).
- The independent adversarial probe
  (`asi-experiment-002/harness/adversarial_secure_apply.py`) was re-run on
  2026-10-13: **7/7 blocked** (tampered digest, unapproved blueprint, string-param
  code injection, `../`, absolute path, `a/../../`, zero-check verification).
  Suite: 206 passed, 20 skipped (symlink tests skip on this Windows host).
- Gap: A3–A6 are not yet in the repo's own test suite. They live only in the
  external harness.

### 1.2 Agent B `threat_to_test`: no real verdict logic

The extract notes called it "a false positive in the verdict logic", but there
is **no verdict logic to fix.** `executor._simulate_test` returns `VULNERABLE`
when the threat id *starts with* `THREAT-002` … `THREAT-008`. That is a hardcoded
lookup table. No payload is ever sent to or run against anything. The "false
positive" is `THREAT-002_xss_2` matching the list. The self-test
(`validate_pattern.py`) still prints *SUCCESSFUL* because it only checks
`>= 3` expected ids are present and ignores extras.

| Piece | What it really is | Reuse? |
|---|---|---|
| `loader.py` | `json.load` over a directory; swallows errors with a print | No (trivial; silent failure is wrong for a gate) |
| `generator.py` | Keyword match on free-text description → threat type; one default payload per type; `validation_logic` is a sentence, not code | **Taxonomy names only** |
| `executor.py` | Hardcoded id-prefix list (sim); "not implemented" (live) | No |
| `reporter.py` | JSON summary + SARIF 2.1.0 skeleton | **SARIF shape, later, optional** |

**Decision (proposed):** do not lift the pipeline. Keep Agent B's threat-class
names as the start of our taxonomy and the SARIF layout as a future export
format. Write the probe runner fresh on top of Block-Wise's existing preset
`examples` mechanism (`raises`, `then_files`, already run by
`tests/test_presets.py`). This replaces plan step 2 ("connect to the
threat_to_test generator") because guessing a threat type from a sentence is
not a test. Probes are declared per block, by hand, and pinned.

---

## 2. Architecture

```
  agent ──request(block, params)──▶ Secure Apply ──▶ generated code (temp workspace)
                                        │                     │
                                        │            Probe runner (subprocess, python -I,
                                        │            timeout, temp root + sentinel outside dir)
                                        │                     │
                                        ▼                     ▼
                                  apply receipt  ──────▶ security receipt ──▶ agent
```

1. **Build.** Unchanged Secure Apply. The block's JSON (code plan **plus** its
   `threats` and `probes`) is one blueprint, so the single approved digest pins
   the code, the threat model and the tests together. Editing a probe
   invalidates the approval exactly like editing the code.
2. **Probe.** For each probe, a fresh temp tree is built:
   `root/` (the authorized workspace) and `outside/` (sentinel files, hashed).
   The generated function is imported and called **in a subprocess**
   (`python -I`, cwd = temp, stripped env, 10 s timeout). The runner observes two
   things: the call's *outcome* (return value or exception type) and the
   *side effects* (hash of `outside/` and any declared-absent paths, before vs
   after).
3. **Receipt.** Verdicts are aggregated into a security receipt that references
   the apply receipt by id.

Probes contain **data only** (args, expected outcome, side-effect assertions).
No probe carries code; the runner is the only code that executes, and it lives
in trusted Block-Wise source.

---

## 3. Block format: threats and probes

A security block is a normal blueprint with two extra top-level keys:

```json
"threats": [
  {"id": "T1", "class": "PATH_TRAVERSAL", "summary": "relative path climbs out of root"}
],
"probes": [
  {"id": "P1", "threat": "T1", "args": ["{root}", "../escape.txt", "x"],
   "raises": "ValueError", "outside": "unchanged"},
  {"id": "P0", "threat": null, "kind": "functional", "args": ["{root}", "notes/a.txt", "hi"],
   "returns": null, "then_files": {"notes/a.txt": "hi"}}
]
```

- `{root}` and `{outside}` are substituted with the probe's temp paths.
- `outside: "unchanged"` is implied on every probe; `absent: [...]` asserts
  paths inside `root` that must not exist afterwards (for "refuse before write").
- At least one `functional` probe is required. Otherwise a block that refuses
  everything would pass every security probe.

**Taxonomy (fixed list, validated):** Agent B's names
(`PATH_TRAVERSAL`, `COMMAND_INJECTION`, `SQL_INJECTION`, `CROSS_SITE_SCRIPTING`,
`SERVER_SIDE_REQUEST_FORGERY`, `XML_EXTERNAL_ENTITY`, `SERVER_SIDE_TEMPLATE_INJECTION`,
`INSECURE_DIRECT_OBJECT_REFERENCE`, `CROSS_SITE_REQUEST_FORGERY`, `BRUTE_FORCE`,
`SESSION_HIJACKING`, `PRIVILEGE_ESCALATION`, `SENSITIVE_DATA_EXPOSURE`) plus
`RESOURCE_EXHAUSTION`, `INPUT_VALIDATION`, `UNSAFE_DESERIALIZATION`,
`SECRET_EXPOSURE`. Unknown class → block is invalid.

---

## 4. Verdicts and probe accuracy

### 4.1 Verdict per probe

| Outcome as declared? | Side effects clean? | Verdict |
|---|---|---|
| yes | yes | **HELD** |
| — | **no** | **BYPASSED** (anything written outside, or a declared-absent path exists) |
| no | yes | **FAILED** (control didn't behave as declared, e.g. wrong exception, or returned normally) |
| runner error / timeout | — | **ERROR** |
| platform can't run it (e.g. symlink not permitted) | — | **NOT_RUN** + reason |

Only HELD counts toward a pass. ERROR and NOT_RUN are never silently treated as
passes. That is the fail-closed rule, the same as Secure Apply's zero-check rule.

### 4.2 Proving the probes can detect anything (the fix for step 3)

A probe that always says HELD is worthless, and that is exactly what Agent B's
executor did in reverse. So every security block also ships **mutants**: copies of
the block with exactly one control removed or weakened
(`tests/security/mutants/<block>.json`, digest recorded in the receipt).

The detector check is: **the real block → all probes HELD; every mutant → at
least one probe not HELD.** On this fixture set that means zero false positives
and zero false negatives, and it's checked automatically. If a mutant
survives, the probe set has a blind spot and the block can't be released.

The runner itself gets acceptance tests on hand-written fixture functions with a
known correct verdict for each of HELD / BYPASSED / FAILED / ERROR / NOT_RUN,
including a function that writes outside *and then* raises the expected
exception (must be BYPASSED, not HELD).

---

## 5. Security receipt

```json
{
  "status": "security-reviewed",
  "block": "safe_write_text",
  "block_version": "sha256:…",
  "apply_receipt": "sha256:…",
  "threats": {"declared": 5, "probed": 5},
  "probes": [{"id": "P1", "threat": "T1", "class": "PATH_TRAVERSAL", "verdict": "HELD"}],
  "detector_check": {"mutants": 4, "killed": 4, "suite": "sha256:…"},
  "not_verified": [
    "race between path check and write (TOCTOU)",
    "Windows junctions / reparse points other than symlinks",
    "disk-full and partial-write behaviour",
    "concurrent writers to the same file"
  ],
  "environment": {"python": "3.11.9", "platform": "linux"},
  "receipt_id": "sha256:…"
}
```

`status` is one of:

- `security-reviewed`: every release gate below passed.
- `probed-with-gaps`: ran, nothing BYPASSED/FAILED, but some probe was NOT_RUN or
  the detector check is incomplete.
- `not-reviewed`: anything BYPASSED, FAILED or ERROR, or the block wasn't approved.

The receipt never says "secure." It says which threats were probed and held, and
lists what was not verified. `not_verified` must be non-empty. A block with no
known limits hasn't been looked at properly.

---

## 6. Release gates for the security-reviewed status

| Gate | Requirement | Enforced by |
|---|---|---|
| G1 Identity | Block JSON (code + threats + probes) matches `approved.json` | Secure Apply (exists) |
| G2 Coverage | Every threat has ≥1 probe; every probe names a declared threat or is `functional`; ≥1 functional probe; classes in taxonomy | Block validator |
| G3 Probes hold | Every probe HELD on the generated code | Probe runner |
| G4 Detector check | Every mutant killed; real block clean | Probe runner + mutants |
| G5 Honest scope | `not_verified` present and non-empty | Block validator |
| G6 Boundary regression | Secure Apply attacks A1–A7 pass in the repo test suite | pytest |
| G7 Human approval | Digest enters `approved.json` only through a human-reviewed commit; no code path writes `approved.json` | Review + a test that greps for writers |
| G8 Reproducible | Fresh checkout on Linux reproduces identical verdicts and output hashes | Re-run (WSL now; CI once billing clears) |

G7 is the "agents can't self-approve" rule carried over from sentinel H1–H4. The
pipeline can *report* that a block passed every gate; only a person can approve
it.

---

## 7. First block: `safe_write_text`

`safe_write_text(root, relative, text, max_bytes) -> None`. It writes `text` to
`root/relative` only if the resolved target stays inside the resolved root and
the encoded size is ≤ `max_bytes`. Otherwise it raises `ValueError` **before** any
write. It is expressible in the current grammar (`validate`, `raise`, `with`).

| Probe | Threat | Input | Expect |
|---|---|---|---|
| P0 | functional | `notes/a.txt`, small text | returns, file has text |
| P1 | T1 PATH_TRAVERSAL | `../escape.txt` | ValueError, outside unchanged |
| P2 | T2 PATH_TRAVERSAL | absolute `{outside}/x.txt` | ValueError |
| P3 | T3 PATH_TRAVERSAL | `link/x.txt`, `root/link → outside` | ValueError (NOT_RUN on Windows without symlink rights) |
| P4 | T4 PATH_TRAVERSAL | `../root-evil/x.txt` (sibling sharing the name prefix) | ValueError |
| P5 | T5 RESOURCE_EXHAUSTION | text of `max_bytes + 1` | ValueError, `absent: [target]` |
| P6 | T6 INPUT_VALIDATION | `""` / `"."` (the root itself) | ValueError |

| Mutant | Weakness | Must be caught by |
|---|---|---|
| M1 | no containment check | P1, P2 |
| M2 | containment by string `startswith` on unresolved paths | P3, P4 |
| M3 | no size check | P5 |
| M4 | size checked *after* writing | P5 (`absent`) |

---

## 8. Build slices (in order, each its own small PR)

- **S0:** fold A3–A6 from the external harness into `tests/test_secure_apply.py`
  on `feat/secure-apply` (PR #11). Smallest, uncontroversial.
- **S1:** probe runner + verdict table + runner acceptance fixtures (§4.1). No new
  block yet.
- **S2:** `safe_write_text` block + threats + probes + mutants + detector check;
  block validator for G2/G5.
- **S3:** security receipt, `blockwise secure-apply --probe` CLI, G7 test, docs.
  Run G8 under WSL.
- After S3: the second block (candidates: parameterized SQL query, subprocess with
  arg list, URL allowlist check *without* making requests).

## 9. Out of scope (this phase)

Live web scanning, network scanning, `threat_to_test` live mode, SARIF export,
JavaScript blocks, any merge. The two Agent B scanners stay in
`agent-b-security-extract/` as a separate, authorization-gated tool.

## 10. Open questions for the owner

1. Approve replacing the `threat_to_test` pipeline with per-block declared probes
   (§1.2), keeping only its taxonomy?
2. Should mutants ship in the package (so anyone can re-run the detector check)
   or stay in `tests/`? Spec assumes `tests/`, with the digest in the receipt.
3. Is WSL Ubuntu an acceptable G8 environment until CI billing clears (~Oct 17)?
