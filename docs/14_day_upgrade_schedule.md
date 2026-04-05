# 14-Day Upgrade Schedule v2

## Goal

This 14-day plan is designed to move toward a **credible international mid-level slot math candidate** profile, not just by improving interview answers, but by building a **compliance-aware validation project** that can serve as a strong showcase.

Main focus areas:

1. **New validation project design and implementation**
2. Compliance knowledge foundation
3. Career narrative reconstruction
4. English expression improvement

Core order:

> **2 → 1 → 3** as the main track  
> **4** is embedded into every day’s output

Reasoning:

- Compliance defines the boundary first
- The new project is the main implementation battlefield
- Career narrative should be rebuilt after compliance and project logic become clearer
- English should be trained through real output, not isolated practice

---

## Daily Time Structure (8 hours/day)

- **Block A – 3h**: Deep main task
- **Block B – 2h**: Secondary main task
- **Block C – 2h**: Output / reconstruction
- **Block D – 1h**: English practice tied to the day’s work

Every day must produce something visible:
- document
- code
- notes
- rewritten narrative
- spoken English output

---

# Week 1 — Set boundaries, define correctness, start the new project

## Day 1

### Block A — 3h  
**Compliance foundation**

Content:
- what fairness means in regulated iGaming
- RNG independence
- predefined outcome model vs runtime manipulation
- red flags: adaptive odds, player-state steering, rerolling to fit a target envelope
- what simulation is for, and what it is not for

Output:
- `docs/compliance_notes_v1.md`
- sections:
  - what must be fixed
  - what must never change at runtime
  - what simulation validates
  - unsafe language list

### Block B — 2h  
**Legacy risk review**

Content:
- list current semantic danger points from Olympus thinking
- identify what must not be carried into the new project
- focus on:
  - control semantics
  - reroll / protect / range filtering style logic
  - result-shaping language
  - report-first mindset

Output:
- `docs/legacy_risk_review.md`
- sections:
  - must abandon
  - can reuse conceptually
  - can reuse technically

### Block C — 2h  
**Career fact整理 v1**

Content:
- only factual整理, no beautification
- split into:
  - early game design growth
  - math ownership period
  - freelance / consulting fragments
  - why now international / regulated path

Output:
- one-page Chinese factual draft

### Block D — 1h  
**English**
- translate 10 compliance keywords into your own English
- record 5 minutes on:
  - “What fairness means in regulated iGaming”

---

## Day 2

### Block A — 3h  
**Compliance: RTP / verification / confidence**

Content:
- empirical RTP vs theoretical RTP
- no-theoretical-RTP case: spec consistency and baseline validation
- sample size and uncertainty
- meaning of confidence intervals
- RTP verification is not just “run many spins”
- volatility and RTP uncertainty must be separated

Output:
- `docs/compliance_notes_v2.md`
- add:
  - RTP verification checklist
  - acceptable deviation notes

### Block B — 2h  
**New project positioning**

Content:
- define how this new project differs from Olympus
- lock the project as:
  - validation system
  - not just simulation/reporting tool
- define what value it should show in hiring context

Output:
- `docs/project_positioning.md`
- sections:
  - what this project is
  - what this project is not
  - why it is stronger than a pure analysis tool

### Block C — 2h  
**Career narrative risk cleanup**

Content:
- what must never be said directly
- what can be reframed as:
  - unregulated market
  - fast-paced production
  - reverse-engineering player experience
  - freelance math consulting

Output:
- 3-column sheet:
  - cannot say
  - can say
  - must rewrite

### Block D — 1h  
**English**
- practice:
  - What is fairness?
  - How do you validate RTP?
  - What is the role of simulation?

---

## Day 3

### Block A — 3h  
**Define system scope**

Content:
- define what the new system validates
- define what it does not validate
- define correctness
- define acceptable deviation
- define the boundary between model validation and live behavior validation

Output:
- `docs/system_scope.md`

### Block B — 2h  
**3-layer verification design**

Content:
- define:
  - implementation layer
  - model layer
  - statistical layer
- for each layer:
  - inputs
  - outputs
  - responsibilities
  - failure examples

Output:
- `docs/verification_layers.md`

### Block C — 2h  
**Career narrative v1 (Chinese)**

Content:
- rewrite the main career story:
  - high-output background
  - self-built validation mindset
  - moving from production-heavy work toward more rigorous validation
  - seeking international regulated environment to grow

Output:
- 500–800 Chinese characters version

### Block D — 1h  
**English**
- explain this career line in English for 3 minutes
- avoid unsafe wording

---

## Day 4

### Block A — 3h  
**Project architecture v1**

Content:
- define target structure:
  - game logic layer
  - simulation layer
  - canonical result
  - metrics layer
  - validation layer
  - optional export layer
  - CLI shell
- make export optional, not central

Output:
- `docs/architecture_v2.md`
- include data flow:
  - config → engine → canonical result → metrics → validation → optional exports

### Block B — 2h  
**Canonical result design**

Content:
- unify fields such as:
  - seed
  - config id
  - mode
  - stake
  - spins
  - raw outcomes
  - metadata / version

Output:
- dataclass or typed dict design in:
  - `docs/canonical_result.md`

### Block C — 2h  
**Career narrative v2 (English skeleton)**

Content:
- convert Chinese story into English bullet skeleton
- only short sentences

Output:
- 3 sections:
  - background
  - transition
  - why now

### Block D — 1h  
**English**
- read and restate the English skeleton
- note down stuck points

---

## Day 5

### Block A — 3h  
**Metrics layer design**

Content:
- define metric bundle:
  - empirical RTP
  - hit frequency
  - payout distribution summary
  - tail concentration
  - optional streak/session proxies
- separate descriptive metrics from validation metrics

Output:
- `docs/metrics_design.md`

### Block B — 2h  
**Statistical layer design**

Content:
- define:
  - variance estimation
  - confidence interval
  - acceptable deviation rule
  - sample size rule
- clarify:
  - simulation baseline vs live data role

Output:
- `docs/statistical_validation.md`

### Block C — 2h  
**Project external description draft**

Content:
- write the new project intro
- banned phrases:
  - guide system behavior
  - adjust probability dynamically
  - influence outcomes over time

Output:
- 150–200 word English project description

### Block D — 1h  
**English**
- practice the project intro until it can be said clearly within 2 minutes

---

## Day 6

### Block A — 3h  
**Minimal engine implementation**

Content:
- build the minimal game logic path:
  - deterministic RNG
  - result generation
  - payout mapping
- no fancy features first
- keep Gate of Olympus-style inspiration, but simplify where needed for clean structure

Output:
- minimal runnable engine files

### Block B — 2h  
**Core API skeleton**

Content:
- define minimal core interfaces such as:
  - `run_simulation(...) -> CanonicalResult`
  - `compute_metrics(result) -> MetricsBundle`
  - `validate_metrics(metrics, baseline) -> ValidationReport`

Output:
- core API skeleton files

### Block C — 2h  
**Career narrative: risky question material**

Content:
- draft Chinese answers for:
  - Why did you leave?
  - Why international iGaming?
  - Why remote?
  - What kind of team are you looking for?

Output:
- Chinese Q&A draft

### Block D — 1h  
**English**
- build English skeleton for 2 of those questions

---

## Day 7

### Block A — 3h  
**Pipeline first pass**

Content:
- connect:
  - engine → canonical result
  - canonical result → metrics
- make one basic case run end-to-end

Output:
- first runnable validation pipeline

### Block B — 2h  
**Week 1 review**

Content:
- check whether project positioning is still correct
- check whether architecture is really validation-first
- identify remaining risks:
  - report-first thinking
  - unsafe semantics
  - weak structure

Output:
- week summary:
  - done
  - not done
  - next risks

### Block C — 2h  
**English output integration**

Content:
- combine:
  - fairness
  - RTP validation
  - new project intro
  - background

Output:
- one-page English interview outline

### Block D — 1h  
**Spoken review**
- speak continuously for 8–10 minutes on this week’s themes

---

# Week 2 — Implement, deepen cognition, make it externally usable

## Day 8

### Block A — 3h  
**Compliance: audit mindset**

Content:
- not legal text memorization
- understand:
  - why auditability matters
  - reproducibility as evidence
  - what labs / regulators conceptually need

Output:
- `docs/audit_mindset.md`

### Block B — 2h  
**Artifact metadata scheme**

Content:
- all outputs should carry:
  - version / git ref if possible
  - seed
  - config
  - stake
  - mode
  - spins
  - timestamp

Output:
- `docs/artifact_metadata.md`

### Block C — 2h  
**Career narrative: English v1**

Content:
- write full English narrative
- still short, logic-first

Output:
- 400–600 word English career narrative

### Block D — 1h  
**English**
- record and replay
- mark unnatural phrasing

---

## Day 9

### Block A — 3h  
**Validation layer implementation**

Content:
- implement:
  - CI calculation
  - deviation check
  - validation report generation
- make the pipeline produce:
  - observed metrics
  - expected range
  - verdict / notes

Output:
- first validation report path runs

### Block B — 2h  
**Test design**

Content:
- define 4 test classes:
  - deterministic replay
  - metrics regression
  - validation rule check
  - edge cases

Output:
- `tests_plan.md`

### Block C — 2h  
**Narrative alignment**

Content:
- make new project, past experience, and job target form one line
- avoid split between “clean project” and “unsafe past wording”

Output:
- aligned bilingual outline

### Block D — 1h  
**English**
- practice:
  - career transition
  - project
  - why international

---

## Day 10

### Block A — 3h  
**Distribution risk cognition**

Content:
- understand and document:
  - tail concentration
  - top-p RTP share
  - losing streak distribution
  - why correct RTP can still mean poor game behavior

Output:
- `docs/distribution_risk.md`

### Block B — 2h  
**Distribution checks in project**

Content:
- define and implement first distribution-level checks
- not only RTP pass/fail
- include:
  - hit frequency
  - tail indicator
  - one concentration metric

Output:
- distribution validation path added

### Block C — 2h  
**Behavioral stories rewrite**

Content:
- write only 3 stories:
  - strongest success
  - one failure / poor fit
  - one transition / growth story

Output:
- STAR skeleton version

### Block D — 1h  
**English**
- tell each story in about 90 seconds

---

## Day 11

### Block A — 3h  
**Live vs simulation gap**

Content:
- define:
  - variance vs structural issue
  - what simulation can explain
  - what only live data can reveal
- clarify why simulation validates the model, not player behavior

Output:
- `docs/live_vs_simulation.md`

### Block B — 2h  
**Player behavior vs math**

Content:
- document:
  - session behavior
  - stake change
  - bonus-buy preference
  - behavior bias vs model assumptions

Output:
- `docs/player_behavior_gap.md`

### Block C — 2h  
**Narrative compression**

Content:
- compress English narrative into:
  - 30 sec
  - 90 sec
  - 3 min

Output:
- 3 versions

### Block D — 1h  
**English**
- say all 3 versions without script

---

## Day 12

### Block A — 3h  
**Multi-mode validation**

Content:
- define how to validate:
  - base mode
  - bonus mode
  - buy bonus mode if present
- understand RTP allocation across modes

Output:
- `docs/multimode_validation.md`

### Block B — 2h  
**Project audit day**

Content:
- review as an external reviewer
- check:
  - unsafe semantics removed
  - clean flow
  - validation-first positioning holds
  - outputs are understandable

Output:
- audit issue list

### Block C — 2h  
**Job-material integration**

Content:
- update resume project description
- update LinkedIn / GitHub project wording

Output:
- application-ready project description

### Block D — 1h  
**English**
- 3 min project + 3 min career

---

## Day 13

### Block A — 3h  
**Documentation rewrite**

Content:
- README
- design
- metrics
- compliance summary
- scope / guarantees / non-goals

Output:
- updated project docs

### Block B — 2h  
**Technical self-mock**

Content:
- ask yourself 20 questions around:
  - validation
  - RTP verification
  - CI
  - model vs behavior
  - project design
- identify weak or dangerous wording

Output:
- weak-answer list

### Block C — 2h  
**Career narrative final version**

Content:
- finalize:
  - intro
  - project
  - why transition
  - why remote
  - why now

Output:
- final bilingual version

### Block D — 1h  
**English**
- full 15-minute self-mock

---

## Day 14

### Block A — 3h  
**Final review: do the four lines close properly?**

Check:
- has the new project become a credible mid-level showcase?
- is compliance knowledge now a minimum working system?
- is the narrative safe and usable?
- can English stably express core content?

Output:
- final gap list

### Block B — 2h  
**Last key fixes**

Content:
- only fix:
  - structural gaps
  - unsafe wording
  - weak explanations
  - broken pipeline parts

Output:
- final cleanup round

### Block C — 2h  
**Prepare next 30-day continuation plan**

Content:
- what to deepen
- what can already be used in applications
- what should wait for real interview feedback

Output:
- `next_30_day_plan.md`

### Block D — 1h  
**English**
- final recording:
  - self intro
  - project
  - fairness / RTP validation

---

# Daily Hard Checks

At the end of every day, answer these 5 questions:

1. Did I produce a saved artifact today?
2. Did I move the new project closer to:
   - semantic safety
   - validation-first structure
   - core API clarity
   - reproducibility
   - testability
3. Did I move my regulated iGaming understanding from vague to explainable?
4. Did I make my career story safer and more credible?
5. Did I do at least 1 hour of output-based English?

---
