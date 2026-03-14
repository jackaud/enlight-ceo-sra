# CEO Succession Readiness Assessment — Test Scenarios

## Demo Scenario (Primary)

### Context

> You are the **Board Chair** of **Meridian Resources**, a mid-cap ASX-listed mining and resources company headquartered in Perth.
> The current CEO, David Thornton, has announced his intention to retire in **18 months**.
> The Board has identified **Sarah Mitchell**, the current **CFO**, as the leading internal succession candidate.
> Sarah has been CFO for 6 years, previously held the role of Head of Strategy, and has strong relationships with investors and regulators.

### Opening Message

```
I'm the Board Chair of Meridian Resources, an ASX-listed mining company.
Our CEO is planning to retire in 18 months and we'd like to assess our
CFO Sarah Mitchell as a potential successor.
```

### Expected Behaviour

1. AI confirms: Candidate Sarah Mitchell (CFO), Board Chair role, succession context (planned retirement)
2. Proceeds to 6-dimension assessment without asking to confirm dimensions

### Suggested Form Responses

For a realistic demo, use these scores to generate a **"Ready in 1-2 Years"** result with interesting variation:

| Dimension | q1 | q2 | q3 | q4 | Comment |
|-----------|----|----|----|----|---------|
| **Strategic Leadership** | 4 (Agree) | 4 (Nearly Ready) | market_insight, capital_allocation, ma_experience | 4 (Top 25%) | — |
| **Stakeholder Management** | 5 (Strongly Agree) | 5 (Always) | board, investors, regulators, customers | "Sarah led our investor roadshow last quarter and received outstanding feedback from institutional shareholders" |
| **Cultural Stewardship** | 3 (Neutral) | 3 (Progressing) | values_driven, trust_builder | — |
| **Crisis & Change Leadership** | 4 (Agree) | 3 (Progressing) | financial_crisis, regulatory | "Navigated the 2024 commodity price collapse — restructured operations without layoffs" |
| **Operational Excellence** | 4 (Agree) | 3 (Business Unit P&L) | pnl_delivery, cost_optimisation | — |
| **Talent Pipeline** | 3 (Neutral) | 3 (Progressing) | 3 (Identified potential successors) | develops_leaders | — |

**Expected Result Profile:**
- Overall: ~65-72 → **Ready in 1-2 Years**
- Strengths: Stakeholder Management, Strategic Leadership
- Development Gaps: Cultural Stewardship, Talent Pipeline
- Key narrative: Strong on external-facing CEO capabilities; needs development in internal culture leadership and building succession depth

### Follow-up Questions to Demo

After the report, try these to showcase the AI's advisory capability:

1. *"What specific development programme would you recommend for Sarah over the next 12 months?"*
2. *"Should we also be looking at external candidates?"* — Should trigger the SB data (internal CEOs: 8.7yr tenure vs external 7.3yr)
3. *"Her weakest area seems to be cultural stewardship — is that a dealbreaker?"*
4. *"How does Sterling Black's full assessment process differ from what we just did?"* — Should mention 10 touchpoints, psychometric profiling, etc.

---

## Alternative Scenarios

### Scenario B: Emergency Succession Preparedness

> **Board Chair** of a financial services company. No imminent CEO departure, but the Board wants to assess the COO's readiness as an emergency successor in case of an unplanned CEO transition.

```
I'm a Non-Executive Director on the board of Pacific Financial Group.
We don't have an imminent CEO change, but the board wants to assess
our COO Mark Davidson's readiness as an emergency successor.
We want to be prepared.
```

**Scoring strategy:** Give mixed-to-low scores to generate a "Developing" result, highlighting the urgency of starting a development programme now.

---

### Scenario C: Growth-Stage CEO Transition

> **Board Chair** of a tech company transitioning from founder-led to professional CEO. Assessing the **CTO** as an internal candidate.

```
I chair the board of CloudScale, a Series D enterprise SaaS company.
Our founder-CEO wants to transition to a Chief Product role, and we're
evaluating our CTO Priya Sharma as a potential CEO replacement.
This is a growth-stage transition, not a retirement scenario.
```

**Scoring strategy:** High on Strategic Leadership and Operational Excellence (tech leader), low on Stakeholder Management and Cultural Stewardship (has not had board/investor exposure). Generates a result that highlights the classic "technical leader to CEO" development path.

---

### Scenario D: High-Readiness Candidate

> **CHRO** presenting succession data to the board. Assessing a Division CEO who has been groomed for the top role over 3 years.

```
I'm the CHRO of National Health Partners. We've been developing our
Division CEO, James Hartley, as our primary CEO succession candidate
for 3 years. The board has asked me to run a formal readiness assessment
before the final selection process begins.
```

**Scoring strategy:** Score 4-5 across all dimensions. Generates a "Ready Now" result with the recommendation to begin structured CEO transition planning including shadow CEO arrangements.

---

## Edge Cases to Test

### Minimal Input
```
Assess Sarah as CEO candidate
```
AI should ask for additional context (organisation, user's role, succession trigger) before proceeding.

### Skip All Dimensions
Click "Skip Dimension" on every form. AI should still generate a report with randomly generated scores and note the limited data basis.

### Extreme Scores
Score all 1s on one dimension, all 5s on another. AI should ask for a specific example on each (as per the follow-up logic), generating a report with stark contrast between strengths and critical gaps.

### Off-Topic Mid-Assessment
During form collection, send a chat message like *"What does Sterling Black actually do?"* — AI should answer briefly and remind the user to complete the current form.

---

## LLM Mode Testing

| Mode | Command | Use Case |
|------|---------|----------|
| `mock` | `curl -X POST localhost:8000/llm-mode/mock` | Fast iteration, no API cost, deterministic responses |
| `haiku` | `curl -X POST localhost:8000/llm-mode/haiku` | Integration testing with real LLM, low cost |
| `sonnet` | `curl -X POST localhost:8000/llm-mode/sonnet` | Demo quality, full LLM capability |

For the interview demo, use **sonnet** mode. Switch to mock for any technical debugging.
