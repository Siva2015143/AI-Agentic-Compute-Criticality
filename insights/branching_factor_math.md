# Understanding the Branching Factor

## Definition

The branching factor b is the mean number of children spawned per call.

Formally, for a population of N calls with offspring counts {c_1, c_2, ..., c_N}:
```
b = (1/N) × sum(c_i)
```

## Why It Matters

The branching factor determines whether recursion terminates or explodes.

Three regimes:

**Subcritical (b < 1)**
- Each generation is smaller than the previous
- Process terminates in finite time
- Expected total calls: 1/(1-b)
- Cost is predictable

**Critical (b = 1)**  
- Each generation has same size on average
- Process continues indefinitely in expectation
- Total calls follow power-law distribution
- Cost has heavy tails

**Supercritical (b > 1)**
- Each generation is larger than previous  
- Process grows exponentially
- Expected total calls diverge
- Cost is unbounded

## Mathematical Derivation

Consider a branching process where each individual produces offspring according to distribution p_k (probability of k children).

The generating function is:
```
f(s) = sum(p_k × s^k) for k=0 to infinity
```

The mean offspring is:
```
b = f'(1) = sum(k × p_k)
```

The probability of eventual extinction satisfies:
```
q = f(q)
```

For b ≤ 1: q = 1 (certain extinction)
For b > 1: q < 1 (positive probability of infinite growth)

## Estimation from Data

Given logs with parent-child relationships:

1. Build call tree from parent_id field
2. Count children for each call
3. Compute sample mean
```python
children_counts = []
for call in logs:
    children = count_calls_with_parent(call.id)
    children_counts.append(children)

b_hat = mean(children_counts)
```

Confidence interval via bootstrap resampling.

## Variance and Critical Slowing

Near criticality, variance explodes as:
```
Var(T) = b × sigma² / (1-b)³
```

where sigma² is variance of offspring distribution.

This cubic divergence is signature of critical transition.

As b approaches 1:
- Mean compute increases as (1-b)^-1
- Variance increases as (1-b)^-3  
- Recovery time increases as (1-b)^-1
- System becomes increasingly unpredictable

## Measured Values

Our experiments found:

- P0 (baseline): b = 0.71, subcritical, stable
- P3 (recursive): b = 0.84, near-critical, high variance
- P6 (agentic): b = 0.84, near-critical, heavy tails

The proximity to b=1 explains observed compute amplification.

## Practical Implications

To maintain control, systems should enforce b < 0.8 through:

- Maximum spawn limits per call
- Exponential backoff on recursion depth
- Budget-based throttling
- Dynamic adjustment based on measured b

Without these controls, natural agentic behavior pushes b toward criticality.