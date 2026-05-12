import os
import math
import streamlit as st
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


load_dotenv()


def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate fixed-rate monthly mortgage payment."""
    monthly_rate = annual_rate / 100 / 12
    n_payments = years * 12

    if principal <= 0:
        return 0.0

    if monthly_rate == 0:
        return principal / n_payments

    return principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / (
        (1 + monthly_rate) ** n_payments - 1
    )


def calculate_metrics(
    purchase_price: float,
    monthly_rent: float,
    down_payment_pct: float,
    annual_interest_rate: float,
    loan_term_years: int,
    annual_taxes: float,
    annual_insurance: float,
    monthly_hoa: float,
    vacancy_pct: float,
    maintenance_pct_of_rent: float,
    closing_costs: float,
) -> dict:
    """Calculate simplified residential rental investment metrics."""

    down_payment = purchase_price * down_payment_pct / 100
    loan_amount = purchase_price - down_payment
    mortgage = monthly_mortgage_payment(loan_amount, annual_interest_rate, loan_term_years)

    monthly_taxes = annual_taxes / 12
    monthly_insurance = annual_insurance / 12
    monthly_vacancy = monthly_rent * vacancy_pct / 100
    monthly_maintenance = monthly_rent * maintenance_pct_of_rent / 100

    monthly_operating_expenses = (
        monthly_taxes
        + monthly_insurance
        + monthly_hoa
        + monthly_vacancy
        + monthly_maintenance
    )

    total_monthly_cost = mortgage + monthly_operating_expenses
    monthly_cash_flow = monthly_rent - total_monthly_cost
    annual_cash_flow = monthly_cash_flow * 12

    annual_noi = (
        monthly_rent * 12
        - (monthly_taxes + monthly_insurance + monthly_hoa + monthly_vacancy + monthly_maintenance) * 12
    )

    cap_rate = annual_noi / purchase_price * 100 if purchase_price else 0
    total_cash_invested = down_payment + closing_costs
    cash_on_cash_return = annual_cash_flow / total_cash_invested * 100 if total_cash_invested else 0

    return {
        "purchase_price": purchase_price,
        "monthly_rent": monthly_rent,
        "down_payment": down_payment,
        "loan_amount": loan_amount,
        "monthly_mortgage_payment": mortgage,
        "monthly_taxes": monthly_taxes,
        "monthly_insurance": monthly_insurance,
        "monthly_hoa": monthly_hoa,
        "monthly_vacancy": monthly_vacancy,
        "monthly_maintenance": monthly_maintenance,
        "monthly_operating_expenses": monthly_operating_expenses,
        "total_monthly_cost": total_monthly_cost,
        "monthly_cash_flow": monthly_cash_flow,
        "annual_cash_flow": annual_cash_flow,
        "annual_noi": annual_noi,
        "cap_rate": cap_rate,
        "total_cash_invested": total_cash_invested,
        "cash_on_cash_return": cash_on_cash_return,
    }


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value:.2f}%"


def build_structured_prompt(metrics: dict) -> str:
    return f"""
You are a real estate investment analyst helping an individual investor evaluate a single residential rental property.

Important instruction:
Do not make a final automated buy-or-don't-buy decision. Instead, produce a decision-support memo that helps the investor understand the deal's financial profile, risks, and next due diligence steps.

Use only the information provided. If something is unknown, say so. Do not invent local market facts, appreciation rates, tax advice, or legal conclusions.

Deal inputs and calculated metrics:
- Purchase price: {format_currency(metrics['purchase_price'])}
- Monthly rent: {format_currency(metrics['monthly_rent'])}
- Down payment: {format_currency(metrics['down_payment'])}
- Loan amount: {format_currency(metrics['loan_amount'])}
- Monthly mortgage payment: {format_currency(metrics['monthly_mortgage_payment'])}
- Monthly taxes: {format_currency(metrics['monthly_taxes'])}
- Monthly insurance: {format_currency(metrics['monthly_insurance'])}
- Monthly HOA: {format_currency(metrics['monthly_hoa'])}
- Monthly vacancy reserve: {format_currency(metrics['monthly_vacancy'])}
- Monthly maintenance reserve: {format_currency(metrics['monthly_maintenance'])}
- Monthly operating expenses excluding debt service: {format_currency(metrics['monthly_operating_expenses'])}
- Total monthly cost including debt service: {format_currency(metrics['total_monthly_cost'])}
- Monthly cash flow: {format_currency(metrics['monthly_cash_flow'])}
- Annual cash flow: {format_currency(metrics['annual_cash_flow'])}
- Annual NOI before debt service: {format_currency(metrics['annual_noi'])}
- Cap rate: {format_percent(metrics['cap_rate'])}
- Total cash invested: {format_currency(metrics['total_cash_invested'])}
- Cash-on-cash return: {format_percent(metrics['cash_on_cash_return'])}

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
"""


def build_baseline_prompt(raw_deal_description: str) -> str:
    return f"""
Analyze this rental property investment:

{raw_deal_description}
"""


def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    if OpenAI is None:
        return "OpenAI package is not installed. Run: pip install openai"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "No OPENAI_API_KEY found. Add your key to a .env file or environment variable. "
            "The calculated metrics above can still be reviewed without the LLM memo."
        )

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": "You are a careful real estate investment analysis assistant. Be structured, practical, and honest about limitations.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content


st.set_page_config(page_title="Rental Deal Memo Generator", page_icon="🏡", layout="wide")

st.title("🏡 Residential Rental Deal Analysis Memo Generator")
st.write(
    "This app turns basic rental property assumptions into a structured investment memo. "
    "It supports decision-making but does not replace human judgment."
)

with st.sidebar:
    st.header("Model Settings")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    use_llm = st.checkbox("Generate GenAI memo", value=True)

st.header("Deal Inputs")

col1, col2 = st.columns(2)

with col1:
    purchase_price = st.number_input("Purchase price ($)", min_value=0.0, value=575000.0, step=5000.0)
    monthly_rent = st.number_input("Expected monthly rent ($)", min_value=0.0, value=2895.0, step=50.0)
    down_payment_pct = st.number_input("Down payment (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0)
    annual_interest_rate = st.number_input("Interest rate (%)", min_value=0.0, value=5.875, step=0.125)

with col2:
    loan_term_years = st.number_input("Loan term (years)", min_value=1, value=30, step=1)
    annual_taxes = st.number_input("Annual property taxes ($)", min_value=0.0, value=12000.0, step=500.0)
    annual_insurance = st.number_input("Annual insurance ($)", min_value=0.0, value=1000.0, step=100.0)
    monthly_hoa = st.number_input("Monthly HOA ($)", min_value=0.0, value=450.0, step=25.0)

col3, col4 = st.columns(2)

with col3:
    vacancy_pct = st.number_input("Vacancy reserve (% of rent)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)

with col4:
    maintenance_pct = st.number_input("Maintenance reserve (% of rent)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)

closing_costs = st.number_input("Estimated closing costs / initial cash costs ($)", min_value=0.0, value=10000.0, step=500.0)

if st.button("Generate Memo"):
    metrics = calculate_metrics(
        purchase_price=purchase_price,
        monthly_rent=monthly_rent,
        down_payment_pct=down_payment_pct,
        annual_interest_rate=annual_interest_rate,
        loan_term_years=loan_term_years,
        annual_taxes=annual_taxes,
        annual_insurance=annual_insurance,
        monthly_hoa=monthly_hoa,
        vacancy_pct=vacancy_pct,
        maintenance_pct_of_rent=maintenance_pct,
        closing_costs=closing_costs,
    )

    st.subheader("Calculated Metrics")

    metric_cols = st.columns(4)
    metric_cols[0].metric("Monthly Cash Flow", format_currency(metrics["monthly_cash_flow"]))
    metric_cols[1].metric("Annual Cash Flow", format_currency(metrics["annual_cash_flow"]))
    metric_cols[2].metric("Cap Rate", format_percent(metrics["cap_rate"]))
    metric_cols[3].metric("Cash-on-Cash Return", format_percent(metrics["cash_on_cash_return"]))

    with st.expander("Show detailed calculations"):
        for key, value in metrics.items():
            if "rate" in key or "return" in key:
                st.write(f"**{key.replace('_', ' ').title()}:** {format_percent(value)}")
            else:
                st.write(f"**{key.replace('_', ' ').title()}:** {format_currency(value)}")

    if use_llm:
        st.subheader("Structured Investment Memo")
        prompt = build_structured_prompt(metrics)

        with st.spinner("Generating memo..."):
            memo = call_llm(prompt, model=model)

        st.markdown(memo)

        with st.expander("Show structured prompt"):
            st.text(prompt)
    else:
        st.info("LLM memo generation is turned off. Review calculated metrics above.")
