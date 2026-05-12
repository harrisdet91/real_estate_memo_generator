# Residential Rental Deal Analysis Memo Generator

## Context, User, and Problem

The target user for this project is an individual real estate investor or homebuyer who is evaluating a single residential property as a potential rental investment. The workflow being improved is the process of turning raw deal assumptions—such as purchase price, expected rent, mortgage rate, taxes, insurance, HOA fees, vacancy, and maintenance assumptions—into a structured investment analysis memo.

This problem matters because residential real estate investments involve large financial commitments and long-term consequences. Many individual investors evaluate deals using ad hoc spreadsheets, mental math, or informal reasoning. As a result, they may focus too heavily on headline rent or purchase price while overlooking key risks such as vacancy, maintenance, financing sensitivity, taxes, HOA costs, or negative cash flow.

This project does **not** attempt to automate the final buy-or-don't-buy decision. Instead, it is designed as a decision-support tool that improves the quality, consistency, and completeness of the analysis used by the investor. The final output is a structured investment memo that helps the user understand the financial profile of a deal, identify risks, and decide what further due diligence is needed.

## Solution and Design

I built a small Streamlit application that takes basic real estate deal inputs and generates a structured residential rental investment memo. The app asks the user to enter key deal parameters, including purchase price, expected monthly rent, down payment percentage, interest rate, loan term, property taxes, insurance, HOA fees, vacancy assumption, maintenance assumption, and estimated closing costs.

The app performs basic deterministic financial calculations in Python, including estimated mortgage payment, monthly operating expenses, monthly cash flow, annual cash flow, cap rate, estimated cash invested, and cash-on-cash return. These calculated metrics are then passed into a structured GenAI prompt, which asks the model to produce a standardized investment memo.

The main GenAI design choice is structured prompt design. Instead of asking the model to generally "analyze this deal," the prompt constrains the output into specific sections: executive summary, key financial metrics, assumptions, strengths, risks, sensitivity considerations, due diligence questions, and recommendation framing. This makes the output more consistent and more useful than a loose prompt.

The system is intentionally simple. It does not use RAG, agents, or multiple models because those design choices are not necessary for this workflow. The goal is to show that a focused prompt plus deterministic calculations can produce a useful workflow artifact: a structured real estate analysis memo.

## Baseline

The baseline is a simpler prompt-only workflow. In the baseline, the user gives the model raw deal inputs and asks: "Analyze this rental property investment." This baseline does not enforce a structured memo format, does not explicitly require a risk checklist, and does not provide deterministic financial calculations before generation.

The improved system is compared against this baseline to evaluate whether the structured workflow produces outputs that are more complete, more consistent, and more useful for decision support.

## Evaluation and Results

Evaluation uses a small set of synthetic residential rental property scenarios. These cases are designed to represent different investment profiles, including a strong cash-flow deal, a marginal deal, a clearly negative cash-flow deal, a high-HOA property, and a high-interest-rate sensitivity case.

Each output is evaluated using a rubric with five dimensions:

1. **Numerical accuracy**: Are the financial metrics correct or reasonably consistent with the given assumptions?
2. **Completeness**: Does the output include the major components expected in an investment memo?
3. **Risk identification**: Does the output identify relevant risks such as vacancy, maintenance, taxes, HOA costs, financing, and market uncertainty?
4. **Clarity and usefulness**: Is the memo easy for an investor to understand and use?
5. **Appropriate decision framing**: Does the output support decision-making without pretending to fully automate the final investment decision?

Each dimension can be scored from 1 to 5. The structured system is expected to outperform the baseline on completeness, risk identification, consistency, and appropriate decision framing. The baseline may sometimes produce useful commentary, but it is more likely to omit key risks or provide an overly confident recommendation.

### Summary of Expected Findings

The structured system works best when the user provides realistic and complete inputs. It produces a more consistent memo than the baseline and more reliably surfaces key risks. However, the system can still break down if the inputs are unrealistic, incomplete, or missing important local market context. It should not be trusted as a substitute for human judgment, property inspection, lender review, tax advice, or local market due diligence.

## Artifact Snapshot

The application provides a form where the user enters deal assumptions. After clicking **Generate Memo**, the app displays:

- calculated financial metrics
- a structured investment memo
- risks and due diligence questions
- recommendation framing such as "strong fundamentals," "borderline," or "high-risk," rather than a final automated buy/don't-buy command

Example input:

- Purchase price: $575,000
- Monthly rent: $2,895
- Down payment: 10%
- Interest rate: 5.875%
- Loan term: 30 years
- Annual property taxes: $12,000
- Annual insurance: $1,000
- Monthly HOA: $450
- Vacancy: 5%
- Maintenance: 5% of rent
- Closing costs: $10,000

Example output: a structured memo explaining that the property may be strategically reasonable for an owner-occupant or long-term hold, but as a standalone rental investment it may have weak near-term cash flow because debt service, taxes, HOA, and operating expenses consume most or all of the rent.

## Setup Instructions

### 1. Clone the repository

```bash
git clone <your-repo-link>
cd real-estate-memo-generator
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API key

Create a `.env` file in the project folder:

```bash
OPENAI_API_KEY=your_api_key_here
```

Do not commit your `.env` file.

### 5. Run the app

```bash
streamlit run app.py
```

## Usage Instructions

1. Open the Streamlit app in your browser.
2. Enter the property assumptions.
3. Click **Generate Memo**.
4. Review the calculated metrics and GenAI-generated memo.
5. Use the memo as a decision-support artifact, not as final investment advice.

## Files

- `app.py`: Streamlit application
- `prompts.md`: baseline and structured prompts
- `eval_cases.json`: synthetic test cases
- `evaluation_rubric.md`: rubric for comparing outputs
- `requirements.txt`: dependencies
- `.gitignore`: excludes `.env` and other local files

## Limitations

This app uses simplified assumptions and does not account for all real-world investment factors. It does not model appreciation, depreciation, tax deductions, local rent comparables, repair history, inspection findings, tenant quality, or transaction-specific financing constraints. It is intended for educational and decision-support purposes only.
