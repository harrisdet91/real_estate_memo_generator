# Prompts

## Baseline Prompt

The baseline prompt is intentionally simple and unconstrained:

```text
Analyze this rental property investment:

Purchase price: $575,000
Expected monthly rent: $2,895
Down payment: 10%
Interest rate: 5.875%
Loan term: 30 years
Annual property taxes: $12,000
Annual insurance: $1,000
Monthly HOA: $450
Vacancy reserve: 5%
Maintenance reserve: 5%
Closing costs: $10,000
```

This baseline may produce useful commentary, but it does not force the model to include a consistent structure, risk checklist, or explicit decision-support framing.

## Structured Prompt

The structured prompt gives the model calculated metrics and requires a standardized memo format:

```text
You are a real estate investment analyst helping an individual investor evaluate a single residential rental property.

Important instruction:
Do not make a final automated buy-or-don't-buy decision. Instead, produce a decision-support memo that helps the investor understand the deal's financial profile, risks, and next due diligence steps.

Use only the information provided. If something is unknown, say so. Do not invent local market facts, appreciation rates, tax advice, or legal conclusions.

Deal inputs and calculated metrics:
[calculated metrics inserted here]

Write a structured investment memo with these exact sections:

1. Executive Summary
2. Key Financial Metrics
3. Assumptions Used
4. Strengths of the Deal
5. Key Risks and Weaknesses
6. Sensitivity Considerations
7. Due Diligence Questions
8. Recommendation Framing

For the Recommendation Framing section, classify the deal as one of:
- Strong fundamentals
- Borderline / requires further diligence
- High-risk / weak fundamentals

Explain the classification, but emphasize that the investor should make the final decision after reviewing local market data, inspection findings, financing terms, and personal investment goals.
```

## Design Rationale

The structured prompt is designed to improve consistency, completeness, and decision usefulness. It also directly addresses the project feedback that the system should not pretend to automate a final investment decision. The goal is to produce a better investment memo, not to tell the user what to buy.
