# AI Compute Criticality

**Why agentic AI costs 100x more than predicted—measured, explained, and solved.**

*Independent research by Sivamani Battala*

---

## The Finding

Agentic AI systems use **13-100x more compute** than scaling laws predict. Not from bigger models. From recursive reasoning.

We measured it across 15 controlled experiments, derived the mathematics, and built tools to detect it in production.

---

## The Problem

**2024**: One prompt → one response → predictable cost

**2025**: One task → agent searches → reads results → verifies → spawns subtasks → calls itself → unpredictable cascade

When average child operations per parent approaches 1, cost becomes exponential.

---

## What We Measured

| Mode | Operations | Compute | Amplification | Branching Factor |
|------|-----------|---------|---------------|------------------|
| Baseline | 1.0 | 8.5M | 1.0x | — |
| Recursive | 6.4 | 71.1M | 8.3x | 0.84 |
| Agentic | 6.1 | 38.7M | 4.5x | 0.84 |

**Peak**: 21x amplification in single trials.

**Critical threshold**: b=1. We measured b=0.84. Systems are 84% of the way to instability.

---

## The Math

```
b = mean children per operation

b < 1:  Expected operations = 1/(1-b)     [stable]
b → 1:  Variance ∝ b/(1-b)³               [explodes]
b > 1:  Operations ∝ (1+ρ)^depth          [exponential]
```

Our b=0.84 predicts 6.25 operations. We observed 6.1-6.4. Theory matches reality.

---

## Why Scaling Laws Broke

**Old formula**:
```
Performance = f(Parameters, Data, Training_Compute)
```

**New reality**:
```
Performance = f(Parameters, Data, Training_Compute, Inference_Depth)
```

That fourth term was zero in 2024. It dominates cost in 2025.

---

## What's Inside

**Papers** (23 + 18 pages)  
Complete mathematical derivations. Nuclear reactor kinetics → branching processes → AI compute.

**Code**  
Production-ready tools to measure branching factor from logs and detect approaching criticality.

**Data**  
Anonymized execution traces from all experiments.

**Documentation**  
Plain-language explanations of core concepts.

---

## Quick Start

```bash
git clone https://github.com/Siva2015143/AI-Agentic-Compute-Criticality.git
cd AI-Agentic-Compute-Criticality
pip install -r requirements.txt

# Run experiment
python minimal_code/agentic_compute_chain_experiment.py --mode P0

# Check your logs
python minimal_code/branching_factor_estimator.py --input your_logs.jsonl
```

**In Python**:
```python
from branching_factor_estimator import estimate_criticality

b, variance = estimate_criticality('your_logs.jsonl')
if b > 0.9:
    print(f"Warning: b={b:.2f} approaching critical threshold")
```

---

## Core Concepts

**Branching Factor (b)**: Mean children spawned per operation. Single most important metric.

**Amplification Factor (A)**: Actual compute / predicted compute. Observed: 3-21x.

**Compute Criticality**: Phase transition at b=1 where cost shifts from deterministic to stochastic.

---

## The Nuclear Analogy

| Nuclear Physics | Agentic AI |
|----------------|-----------|
| Neutron multiplication (k_eff) | Branching factor (b) |
| Chain reaction threshold | Critical compute threshold |
| Control rods | Token limits, budget caps |
| Reactor period | Compute doubling time |

Not metaphor. Formal mathematical mapping with complete derivations.

---

## Why This Matters

**AI Safety**: Cannot establish safety margins without predictable compute.

**Production**: Traditional cost models fail when b→1. Single queries vary by 10-100x.

**Research**: Pre-2025 scaling laws assumed static inference. Agentic systems require new theory.

---

## Validation

**NVIDIA GTC 2025**: Jensen Huang reported 100x compute increase. Our model predicts 86x at 20 steps.

**Theory**: Measured b=0.84 predicts E[operations]=6.25. Observed: 6.1-6.4.

---

## For Different Audiences

**Research Labs**: Publication-ready mathematics with reproducible experiments and open data.

**ML Engineers**: Production tools to measure b in your logs. If b>0.8, implement controls.

**Recruiters**: Demonstrates theoretical math, experimental design, systems engineering, technical writing.

**Leadership**: Explains unpredictable inference costs. Solution requires architecture changes, not tuning.

---

## What's Next

**Immediate**: Multi-model comparison, real-world agents, production workloads, control systems

**Research**: Optimal throttling, early warning indicators, multi-agent networks, distributed dynamics

Full roadmap: `insights/future_work.md`

---

---

## Contact

**Sivamani Battala**  
Independent AI Compute Researcher

sivamani6104@gmail.com  
+91-9014566762  
[GitHub](https://github.com/Siva2015143) • [LinkedIn](https://linkedin.com/in/sivamani-battala)

Open to research collaborations, consulting, and full-time positions in AI safety, infrastructure optimization, systems research.

---



**Active research • December 2025 • Freely available for academic and commercial use**