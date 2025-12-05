# The Compute Chain Reaction

## The Problem

Traditional LLM inference is deterministic and bounded:
```
User: "Summarize this document"
Model: [single forward pass] → [output tokens] → Done
Cost: Fixed, predictable
```

Agentic AI introduces recursion:
```
User: "Research this topic and write a report"
Agent:
  Step 1: Search (spawns web tool)
  Step 2: Read results (spawns multiple fetches)  
  Step 3: Extract facts (spawns analysis)
  Step 4: Cross-reference (spawns more searches)
  Step 5: Synthesize (spawns draft generation)
  
Cost: Variable, potentially unbounded
```

## The Nuclear Analogy

In nuclear fission, one uranium atom splits and releases 2-3 neutrons. Those neutrons strike other atoms, causing further splits. This is a branching process.

If each generation produces more neutrons than the previous generation, you get a chain reaction. The critical point is when each fission produces exactly one fission in the next generation on average.

In agentic AI, one LLM call can spawn multiple child calls. Those children can spawn their own children. This is also a branching process.

If each call spawns one or more children on average, you get computational chain reaction. The critical point is when the branching factor equals one.

## Mathematical Statement

Let b = mean number of child calls per parent call.

Expected total calls: E[T] = 1/(1-b) for b < 1

When b approaches 1:
- Expected calls diverge to infinity
- Variance explodes as (1-b)^-3  
- Cost becomes unpredictable

This is compute criticality.

## Observed Behavior

Our experiments measured b = 0.84 for recursive agentic modes. This is 84% of the way to criticality.

At this operating point:
- Mean calls increased from 1 to 6.4
- Total compute increased 8-15x
- Some trials showed 21x amplification  
- Variance increased by order of magnitude

## Why Traditional Scaling Laws Failed

The Kaplan and Chinchilla scaling laws assumed:
```
Compute = Parameters × Tokens × Constant
```

This holds for single-pass inference. It breaks for recursive agents:
```
Compute = Parameters × Tokens × (1 + b + b² + b³ + ...)
```

When b is small, the geometric series converges and cost remains predictable.

When b approaches 1, the series diverges.

## Real-World Implications

Consider a production system processing 1 million queries per day.

With traditional inference:
- Cost per query: $0.002
- Daily cost: $2,000
- Predictable, plannable

With agentic inference at b=0.84:
- Mean cost per query: $0.016 (8x increase)
- But variance is high: some queries cost $0.042 (21x)
- Daily cost: $16,000 ± $8,000
- Unpredictable, unplannable

## The Control Challenge

Nuclear reactors use control rods to absorb neutrons and keep k_eff below 1.

Agentic systems need analogous controls:
- Token limits (hard caps)
- Budget enforcement (kill switch)
- Depth restrictions (prevent deep recursion)
- Rate limiting (slow propagation)

But these are reactive, not predictive. We cannot forecast which queries will explode before execution.

This is the fundamental problem of compute criticality.