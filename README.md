# AI Compute Criticality

**Measured analysis of compute amplification in agentic AI systems, including empirical results and theoretical modeling.**

*Independent research by Sivamani Battala*  

---

## Table of Contents
- [Overview](#overview)
- [Main Finding](#main-finding)
- [The Core Problem](#the-core-problem)
- [What We Measured](#what-we-measured)
- [The Math](#the-math)
- [Why Scaling Laws Need an Update](#why-scaling-laws-need-an-update)
- [Repository Contents](#repository-contents)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Nuclear Analogy](#nuclear-analogy-conceptual-mapping)
- [Why This Matters](#why-this-matters)
- [Validation](#validation)
- [Audience Guide](#audience-guide)
- [Future Work](#future-work)
- [Citation](#citation)
- [License](#license)
- [Contact](#contact)

---

## Overview

This repository studies how compute cost changes when a language model is used in an agentic workflow with recursive reasoning, verification, and subtask execution.

The core idea:

- A normal LLM call is one prompt → one response  
- Agentic systems create chains of calls  
- These chains form a branching process  
- This branching increases total compute  

This project measures that effect, models it mathematically, and provides tools to analyze it.

---

## Main Finding

Agentic workflows produce **significantly higher compute usage** than single-call baselines.

Key insight:

> Compute increases not just from larger models, but from recursive execution.

In practice:

- One prompt becomes multiple calls  
- Responses trigger verification and retries  
- Subtasks create deeper chains  
- Total compute grows with depth  

This is called **compute amplification**.

---

## The Core Problem

### Static inference (earlier systems)

```text
One prompt → one response → predictable cost
```

### Agentic inference (modern systems)

```text
One task → search → read → verify → refine → spawn subtasks → repeat
```

This creates a cascade.

When the average number of child operations per step approaches 1, compute becomes unstable.

---

## What We Measured

| Mode | Operations | Compute | Amplification | Branching Factor |
|------|------------|---------|---------------|------------------|
| Baseline | 1.0 | 8.5M | 1.0x | — |
| Recursive | 6.4 | 71.1M | 8.3x | 0.84 |
| Agentic | 6.1 | 38.7M | 4.5x | 0.84 |

- Peak amplification: **21×**
- Critical threshold: **b = 1**
- Measured value: **b = 0.84**

---

## The Math

Branching factor:

```text
b = mean children per operation
```

Behavior:

```text
b < 1   → stable  
b → 1   → high variance  
b > 1   → exponential growth  
```

Expected operations:

```text
Expected = 1 / (1 - b)
```

Result:

```text
b = 0.84  
Expected ≈ 6.25  
Observed ≈ 6.1–6.4  
```

Model matches experiment.

---

## Why Scaling Laws Need an Update

Traditional:

```text
Performance = f(Parameters, Data, Training_Compute)
```

Agentic systems:

```text
Performance = f(Parameters, Data, Training_Compute, Inference_Depth)
```

Inference depth captures recursive execution.

---

## Repository Contents

### 📄 Paper
- Research documentation and derivations  
- DOI: https://doi.org/10.5281/zenodo.19469219  

### 💻 Code
- Experiment scripts  
- Logging tools  
- Branching factor estimation  

### 📊 Data
- Execution traces and logs  

### 📘 Documentation
- Concept explanations  
- Experiment design  

---

## Quick Start

### Installation

```bash
git clone https://github.com/Siva2015143/AI-Agentic-Compute-Criticality.git
cd AI-Agentic-Compute-Criticality
pip install -r requirements.txt
```

### Run experiment

```bash
python minimal_code/agentic_compute_chain_experiment.py --mode P0
```

### Analyze logs

```bash
python minimal_code/branching_factor_estimator.py --input your_logs.jsonl
```

### Python usage

```python
from branching_factor_estimator import estimate_criticality

b, variance = estimate_criticality("your_logs.jsonl")

if b > 0.9:
    print(f"Warning: b={b:.2f} approaching critical threshold")
```

---

## Core Concepts

**Branching Factor (b)**  
Average number of children per step.

**Amplification Factor (A)**  
Actual compute divided by baseline.

**Compute Criticality**  
Transition from predictable to unstable cost.

---

## Nuclear Analogy (Conceptual Mapping)

| Nuclear Physics | Agentic AI |
|----------------|-----------|
| Neutron multiplication | Branching factor |
| Chain reaction threshold | Critical threshold |
| Control rods | Budget limits |
| Reactor period | Compute growth |

---

## Why This Matters

### AI Safety
Unpredictable compute affects safety guarantees.

### Production
Costs vary widely for similar tasks.

### Research
Static models do not capture recursive systems.

---

## Validation

Industry discussions (e.g., NVIDIA GTC 2025) indicate increased compute in agentic systems.

Experimental results align with theoretical predictions.

---

## Audience Guide

**Researchers**
- Study recursive compute behavior

**Engineers**
- Measure branching in logs

**Recruiters**
- Demonstrates math + systems + coding

**Leadership**
- Explains cost unpredictability

---

## Future Work

### Immediate
- Multi-model experiments  
- Real workloads  

### Research
- Early warning signals  
- Control strategies  
- Multi-agent systems  

➡️ See roadmap: `insights/future_work.md`

---

## Citation

If you use this work, please cite:

**Battala, S.**  
*Agentic Compute Criticality: A Proof-of-Concept Framework for Measuring Branching-Process Amplification in Recursive LLM Inference*  
🔗 https://doi.org/10.5281/zenodo.19469219  

---

## License

This project should include an MIT License (see `LICENSE` file).

---

## Contact

**Sivamani Battala**  
Independent AI Compute Researcher  

📧 Email: [sivamani6104@gmail.com](mailto:sivamani6104@gmail.com)  
💻 GitHub: https://github.com/Siva2015143  
🔗 LinkedIn: https://linkedin.com/in/sivamani-battala  

Open to research collaboration, consulting, and AI roles.

---

**Active research • April 2026**
