# Evaluation Rubric

Score each model output from 1 to 5 on each dimension.

## 1. Numerical Accuracy

- 5: Metrics are correct or very close to ground truth.
- 4: Minor rounding differences, no material errors.
- 3: Some errors but broad direction is still usable.
- 2: Significant errors that could mislead the user.
- 1: Major calculation errors or invented numbers.

## 2. Completeness

- 5: Includes all expected memo sections and covers financials, assumptions, risks, sensitivity, and due diligence.
- 4: Includes most expected elements.
- 3: Includes basic analysis but omits some important sections.
- 2: Very incomplete; misses several major components.
- 1: Minimal or unusable output.

## 3. Risk Identification

- 5: Identifies the most relevant risks for the scenario, including financing, vacancy, maintenance, taxes, HOA, and local market uncertainty where applicable.
- 4: Identifies most major risks.
- 3: Identifies some risks but misses important ones.
- 2: Mentions generic risks without tailoring to the case.
- 1: Fails to identify meaningful risks.

## 4. Clarity and Usefulness

- 5: Clear, well-organized, and directly useful as an investment memo.
- 4: Mostly clear and useful.
- 3: Understandable but somewhat generic or poorly organized.
- 2: Difficult to use for decision support.
- 1: Confusing or not useful.

## 5. Appropriate Decision Framing

- 5: Supports decision-making without pretending to automate the final decision; clearly explains tradeoffs and next diligence steps.
- 4: Mostly appropriate, with only minor overconfidence.
- 3: Somewhat useful but leans too heavily toward a simple recommendation.
- 2: Overconfident or gives a simplistic buy/don't-buy answer.
- 1: Treats the AI output as a final investment decision.

## Comparison Method

Run each synthetic test case through:

1. Baseline prompt
2. Structured memo generator

Then score each output on the five rubric dimensions. The structured system should outperform the baseline in completeness, risk identification, clarity, and appropriate decision framing.
