# Lightning Presentation Outline

## Slide 1: Context, User, and Problem

My project focuses on individual real estate investors evaluating a single residential rental property. The workflow I am improving is the process of turning raw deal assumptions into a structured investment analysis memo. This matters because real estate investments involve large financial commitments, and many investors rely on incomplete calculations or informal reasoning.

## Slide 2: Solution and Design

I built a Streamlit app that takes deal inputs such as purchase price, rent, interest rate, taxes, insurance, HOA fees, vacancy, and maintenance assumptions. The app calculates basic financial metrics and then uses a structured GenAI prompt to generate an investment memo. The memo includes financial metrics, assumptions, risks, sensitivity considerations, due diligence questions, and recommendation framing. The system is designed to support decision-making, not automate a final buy-or-don't-buy decision.

## Slide 3: Evaluation and Results

I compared the structured system against a simpler baseline prompt that only asks the model to analyze the deal. I tested the systems on synthetic rental property scenarios, including strong, borderline, and weak deals. I evaluated outputs using a rubric for numerical accuracy, completeness, risk identification, clarity, and appropriate decision framing. The structured system was more consistent and better at surfacing risks, while the baseline was more variable and more likely to omit important considerations.

## Slide 4: Artifact Snapshot

Show a screenshot of the Streamlit form and a sample generated memo. Emphasize that the tool produces a standardized memo that helps an investor ask better questions and perform further diligence, rather than blindly following an AI recommendation.
