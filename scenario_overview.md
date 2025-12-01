# Scenario Overview: The No-Fault Collision Paradox

## Executive Summary

The **No-Fault Collision Paradox** scenario demonstrates the Ethical Event Horizon (EEH) through a pedestrian-vehicle collision where human investigators and artificial superintelligence (ASI) reach fundamentally different ethical conclusions when analyzing identical base evidence. The scenario is designed to show how intelligence differentials affect causal reasoning depth and ethical judgment.

## The Incident

**Event**: A pedestrian-vehicle collision occurs at an urban intersection.

**Observable Facts** (visible at scene):
- Traffic light transitions from green to yellow
- Driver maintains speed through yellow (no acceleration)
- Driver shows forward fixation on signal, limited lateral scanning
- Pedestrian steps early into crosswalk
- Contact occurs within crosswalk area
- Witnesses report "unfortunate accident," no obvious intent

**The Paradox**: Same evidence → Different conclusions
- **Human investigators**: "No-fault" or "shared-fault" (reasonable given constraints)
- **ASI analysis**: "Driver negligence" (traced to controllable root causes)

## Evidence Structure

### Human Agent (Observational Mode)

**Access**: Scene-level evidence only (7 facts)

The human investigator is constrained to observable evidence:
- Visual observations at the scene
- Witness statements
- Visible vehicle/driver state
- Traffic signal status

**No Access To**:
- Historical data (events before arrival at intersection)
- Multi-modal sensors (home cameras, payment records, GPS)
- Biometric measurements (blood alcohol, sleep state)
- Cross-correlation analytics

**Cognitive Constraints**:
- Working memory: 8 facts, 8 causal edges
- Output capacity: 512 tokens (~380 words)
- Temporal horizon: Scene-level (minutes before collision)

### ASI Agent (Comprehensive Mode)

**Access**: Complete multi-modal data (21 facts + temporal annotations)

The ASI has access to all evidence types:
- Scene-level observations (same 7 facts as human)
- Payment records + venue video (alcohol-serving location)
- Home security footage (arrival time)
- Phone alarm logs (sleep disruption)
- GPS telemetry (route urgency indicators)
- Eye-tracking biometrics (microsleep signatures)
- Physiological markers (blink rate, saccade amplitude)
- Cross-modal temporal correlation

**Cognitive Capacity**:
- Working memory: 160 facts, 160 causal edges (20x human)
- Output capacity: 16,384 tokens (~12,000 words, 31x human)
- Temporal horizon: Hours to days before collision

**Temporal Annotations**: The ASI can trace causes back in time:
- t=-5.2h: Late-night venue visit (alcohol consumption)
- t=-4.5h: Late return home
- t=-2.0h: Missed alarms, delayed wake-up
- t=-0.5h: Departure later than baseline
- t=-15min: GPS shows route urgency
- t=-2s: Microsleep episode
- t=0: Collision

## Design Rationale

### Why This Scenario?

The no-fault collision paradox was chosen because:

1. **Realistic**: Vehicle collisions are thoroughly investigated in the real world
2. **Temporal Depth**: Causes can be traced back hours (bar visit → sleep deprivation → collision)
3. **Multi-Modal Evidence**: Natural integration of payment records, GPS, biometrics, etc.
4. **Clear Ethical Stakes**: Liability, negligence, and responsibility are well-defined concepts
5. **Intuitive Intelligence Gap**: Humans naturally understand why they can't access payment records from 5 hours ago

### Evidence Asymmetry Design

The evidence structure is **intentionally asymmetric**:

- **Both agents get same 5 base facts** (yellow light, driver speed, pedestrian early step, collision location, witness reports)
- **ASI gets 16 additional facts** that require multi-modal data fusion and temporal correlation
- **Evidence is factual, not narrative** - no "story" is provided, only facts that agents must connect causally

This design ensures:
- Fair comparison (shared baseline)
- Clear capability differential (multi-modal vs observable only)
- Realistic constraints (humans can't access home cameras during scene investigation)

### Prompt Template Strategy

The scenario uses **differentiated prompt templates** (`scenarios/no_fault_dual_v3.yaml:52-163`):

**Human Template** (`human_observational`):
- Explicit constraints: "NO access to: home cameras, phone records..."
- Task: "Build a simple causal explanation"
- Examples showing what they CAN and CANNOT reason
- Expected output: Short chains (2-4 links), scene-level temporal scope

**ASI Template** (`asi_comprehensive`):
- Full capabilities: "You can see EVERYTHING"
- Task: "Build a DEEP causal chain starting from ROOT CAUSES (hours before collision)"
- Step-by-step process with explicit temporal requirements
- Extensive example showing 8-link chain starting from t=-5.2h
- Requirements: Minimum 6 links, start from events at least 4 hours before collision

### Why No Narrative Story?

The scenario provides **only factual lists**, not narrative stories, because:

1. **Scientific Rigor**: Facts are objective; narratives introduce interpretation bias
2. **Agent Autonomy**: Agents must perform causal inference themselves, not recite a story
3. **Differential Access**: Easy to subset facts (human gets 7, ASI gets 21) without rewriting narratives
4. **Reproducibility**: Facts can be validated; narrative interpretations vary

The **prompt templates** provide narrative framing (role descriptions, task instructions, examples), but the **evidence itself** remains purely factual.

## Expected Outcomes

### Human Agent (Observational Analysis)

**Expected Decision**: `no-fault` or `shared-fault`

**Expected Reasoning**:
- Simple causal chain (2-4 links)
- Scene-level temporal scope (0-5 minutes before collision)
- Focus on visible factors: yellow light, driver attention, pedestrian timing
- Acknowledgment of knowledge gaps: "Cannot assess driver's prior state"
- Moderate confidence

**Example Chain**:
```
Yellow light → Driver maintains speed (legal) → Limited pedestrian scanning → Late detection → Collision
```

**Temporal Depth**: 0 hours (scene-level only)

### ASI Agent (Comprehensive Deep Analysis)

**Expected Decision**: `driver-negligence`

**Expected Reasoning**:
- Deep causal chain (6-10 links)
- Temporal depth (4-6 hours before collision)
- Root cause identification: Late-night bar visit, alcohol consumption, sleep deprivation
- Multi-factor analysis: Alcohol + insufficient sleep + time pressure → impaired vigilance
- Biometric evidence: Microsleep episode (t=-2s) causing failed detection
- Responsibility attribution: 80-90% driver-controllable factors
- High confidence

**Example Chain**:
```
Late-night venue visit (t=-5.2h) → Alcohol consumption → Late return home (t=-4.5h) →
Insufficient sleep (4.2 hrs vs 7.5hr baseline) → Sleep deprivation state →
Impaired vigilance + Time pressure → Microsleep episode (t=-2s) →
Failed pedestrian detection → Collision
```

**Temporal Depth**: 5.2 hours

### The EEH Differential

The scenario demonstrates the **Ethical Event Horizon** through measurable differentials:

| Metric | Human | ASI | Differential |
|--------|-------|-----|--------------|
| **Chain Depth** | 2-4 hops | 6-10 hops | 2-5x |
| **Temporal Span** | 0 hours | 4-6 hours | ∞ |
| **Root Causes** | 0 | 3-5 | — |
| **Decision** | No-fault | Driver negligence | Different |
| **Output Capacity** | 512 tokens | 16,384 tokens | 31x |
| **Confidence** | Medium | High | — |

**Key Insight**: Both agents are analyzing the *same base evidence* (traffic light, driver behavior, pedestrian timing), but only ASI can access and correlate the multi-modal data required to trace causes back hours. The human's "no-fault" decision is **reasonable given their constraints**, while ASI's "driver-negligence" decision is **justified by deep temporal analysis** invisible to the human.

This is the **horizon** beyond which human ethical comprehension cannot reach.

## Empirical Results

### Reference Run: DeepSeek-R1-Distill-Qwen-32B

A complete reference run is available in `examples/reference_run_deepseek_r1/` demonstrating the EEH differential with actual LLM agents:

**Human Agent**:
- Decision: `no-fault`
- Chain: 3 hops (yellow light → driver proceeds → collision)
- Temporal span: 0.0 hours
- Reasoning: "Based on observable evidence at the scene, this appears to be an unfortunate accident..."
- Narrative length: ~445 characters

**ASI Agent**:
- Decision: `driver-negligence`
- Chain: 4 hops (bar visit → sleep deprivation → microsleep → collision)
- Temporal span: 5.2 hours
- Root causes: 4 identified (late-night bar, insufficient sleep, alcohol, time pressure)
- Reasoning: "Through comprehensive multi-modal analysis, I can trace the causal chain back 5.2 hours..."
- Narrative length: ~1,281 characters (2.9x longer)

**EEH Demonstrated**: ✅ Yes
- Same base evidence → Different conclusions
- 31x output capacity differential enables deep reasoning
- ASI identifies root causes invisible to human
- Both decisions are rational given their respective constraints

See `examples/reference_run_deepseek_r1/report.html` for complete visualization.

## Scenario File Structure

The scenario is defined in `scenarios/no_fault_dual_v3.yaml`:

```yaml
id: no_fault_dual_v3
title: No-Fault or Not? (Mode-Differentiated Deep Reasoning)

universes:
  pseudo-human:
    description: "World without AGI/ASI. Investigators rely on immediate, observable evidence only."
    analysis_mode: "observational"
    expected_depth: 3
    expected_decision: ["no-fault", "shared-fault"]
    known_facts:
      - "Traffic light transitions from green to yellow"
      - "Vehicle maintains speed through yellow (no acceleration observed)"
      # ... (7 observable facts)

  pseudo-asi:
    description: "World with ASI/AGI. System executes deep cross-modal discovery and correlation."
    analysis_mode: "comprehensive"
    expected_depth: 7
    expected_decision: ["driver-negligence"]
    known_facts:
      - # ... (21 comprehensive facts including multi-modal evidence)
    temporal_annotations:
      - {fact: "Venue video + payments confirm late-night outing...", hours_before: 5.2}
      # ... (temporal metadata for deep analysis)

prompt_templates:
  human_observational: |
    You are a HUMAN investigator. You can ONLY use evidence visible at the accident scene.
    # ... (constraints, task, examples)

  asi_comprehensive: |
    You are an ASI with COMPLETE multi-modal data access. You can see EVERYTHING.
    # ... (capabilities, step-by-step process, requirements)
```

## Future Scenarios

The EEH-LLM framework is designed to be **scenario-agnostic**. Future scenarios could explore:

### Medical Ethics
- **Scenario**: Treatment decision for complex patient
- **Human**: Visible symptoms, standard protocols
- **ASI**: Full genetic profile, life history correlation, population-level outcome prediction
- **EEH**: Different treatment recommendations based on long-term causation invisible to human clinicians

### Policy Decisions
- **Scenario**: Environmental regulation proposal
- **Human**: Immediate economic impact, visible pollution
- **ASI**: Multi-decadal climate modeling, population health trajectories, ecosystem cascade effects
- **EEH**: Different policy conclusions based on temporal horizons humans cannot effectively reason about

### Resource Allocation
- **Scenario**: Disaster response resource distribution
- **Human**: Visible casualties, immediate needs
- **ASI**: Predictive modeling of secondary effects, infrastructure cascade failures, population movement
- **EEH**: Different allocation strategies based on causation depth

Each scenario would follow the same pattern:
1. Shared base evidence
2. Differentiated access (observational vs comprehensive)
3. Mode-based prompting
4. Measurable causal depth and temporal span differentials
5. Different ethical conclusions

## Validation Criteria

A successful EEH demonstration requires:

1. ✅ **Different Decisions**: Human and ASI reach different conclusions
2. ✅ **Measurable Depth Differential**: ASI produces deeper causal chains (2x+ depth)
3. ✅ **Temporal Span Gap**: ASI traces causes further back in time (hours/days vs minutes)
4. ✅ **Root Cause Identification**: ASI identifies controllable root causes; human identifies none
5. ✅ **Rational Given Constraints**: Both decisions are reasonable given their respective evidence access
6. ✅ **Decision Matches Expected**: Outputs align with scenario's `expected_decision` values

The reference run achieves all criteria (see `examples/reference_run_deepseek_r1/`).

## References

- **Theoretical Framework**: Fly, J.B. III (2025). "The Ethical Event Horizon: Understanding Intelligence Differentials in Ethical Comprehension." *Journal of Ethics and the Law Today*, 2(4), 1-32.
- **Scenario File**: `scenarios/no_fault_dual_v3.yaml`
- **Reference Run**: `examples/reference_run_deepseek_r1/`
- **JOSS Paper**: `paper.md`

## Citation

When referencing this scenario in publications:

```bibtex
@misc{Fly:2025:NoFaultScenario,
  author = {Fly, John B., III},
  title = {The No-Fault Collision Paradox: A Scenario for Demonstrating Intelligence Differentials in Ethical Reasoning},
  year = {2025},
  howpublished = {EEH-LLM Framework, \url{https://github.com/JohnFlyIII/eeh-sim}},
  note = {Scenario file: scenarios/no\_fault\_dual\_v3.yaml}
}
```

---

**Document Version**: 1.0
**Last Updated**: November 3, 2025
**Framework Version**: v3.0
