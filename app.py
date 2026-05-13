import os
import streamlit as st
from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

load_dotenv()

st.set_page_config(
    page_title="Residential Rental Deal Memo Generator",
    page_icon="🏡",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.2rem; font-weight: 750; margin-bottom: 0.2rem;}
    .subtitle {font-size: 1.05rem; color: #666; margin-bottom: 1.5rem;}
    .metric-card {padding: 1rem; border: 1px solid #e6e6e6; border-radius: 14px; background-color: #ffffff; box-shadow: 0 1px 2px rgba(0,0,0,0.04); min-height: 100px;}
    .metric-label {color: #666; font-size: 0.85rem; margin-bottom: 0.25rem;}
    .metric-value {font-size: 1.45rem; font-weight: 700;}
    .classification-strong {padding: 1rem; border-radius: 14px; border: 1px solid #b7e4c7; background-color: #f0fff4; color: #1b4332; font-weight: 650; margin-bottom: 0.75rem;}
    .classification-borderline {padding: 1rem; border-radius: 14px; border: 1px solid #ffe8a3; background-color: #fffbea; color: #744210; font-weight: 650; margin-bottom: 0.75rem;}
    .classification-risk {padding: 1rem; border-radius: 14px; border: 1px solid #f5c2c7; background-color: #fff5f5; color: #842029; font-weight: 650; margin-bottom: 0.75rem;}
    .small-muted {color: #666; font-size: 0.9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def monthly_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    monthly_rate = annual_rate / 100 / 12
    n_payments = years * 12
    if principal <= 0:
        return 0.0
    if monthly_rate == 0:
        return principal / n_payments
    return principal * (monthly_rate * (1 + monthly_rate) ** n_payments) / ((1 + monthly_rate) ** n_payments - 1)


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
    down_payment = purchase_price * down_payment_pct / 100
    loan_amount = purchase_price - down_payment
    mortgage = monthly_mortgage_payment(loan_amount, annual_interest_rate, loan_term_years)

    monthly_taxes = annual_taxes / 12
    monthly_insurance = annual_insurance / 12
    monthly_vacancy = monthly_rent * vacancy_pct / 100
    monthly_maintenance = monthly_rent * maintenance_pct_of_rent / 100

    monthly_operating_expenses = monthly_taxes + monthly_insurance + monthly_hoa + monthly_vacancy + monthly_maintenance
    total_monthly_cost = mortgage + monthly_operating_expenses
    monthly_cash_flow = monthly_rent - total_monthly_cost
    annual_cash_flow = monthly_cash_flow * 12
    annual_noi = monthly_rent * 12 - monthly_operating_expenses * 12
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


def call_llm(prompt: str, model: str = "gpt-4o-mini") -> str:
    if OpenAI is None:
        return "OpenAI package is not installed. Run: pip install openai"

    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = None

    api_key = api_key or os.getenv("OPENAI_API_KEY")

    if not api_key:
        return (
            "No OPENAI_API_KEY found. Add your key to Streamlit Secrets or a local .env file. "
            "The calculated metrics above can still be reviewed without the GenAI memo."
        )

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": "You are a careful real estate investment analysis assistant. Be structured, practical, and honest about limitations."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


def infer_classification_from_metrics(metrics: dict) -> str:
    monthly_cash_flow = metrics["monthly_cash_flow"]
    coc = metrics["cash_on_cash_return"]
    cap_rate = metrics["cap_rate"]
    if monthly_cash_flow > 200 and coc >= 6 and cap_rate >= 6:
        return "Strong fundamentals"
    if monthly_cash_flow < -250 or coc < 0 or cap_rate < 4:
        return "High-risk / weak fundamentals"
    return "Borderline / requires further diligence"


def extract_classification(memo: str, metrics: dict) -> str:
    memo_lower = memo.lower()
    if "strong fundamentals" in memo_lower:
        return "Strong fundamentals"
    if "high-risk" in memo_lower or "high risk" in memo_lower or "weak fundamentals" in memo_lower:
        return "High-risk / weak fundamentals"
    if "borderline" in memo_lower or "requires further diligence" in memo_lower:
        return "Borderline / requires further diligence"
    return infer_classification_from_metrics(metrics)


def show_classification_banner(classification: str) -> None:
    if classification == "Strong fundamentals":
        css_class = "classification-strong"
        explainer = "The deal appears to have attractive financial fundamentals based on the provided assumptions, but still requires independent due diligence."
    elif classification == "High-risk / weak fundamentals":
        css_class = "classification-risk"
        explainer = "The deal shows meaningful financial weakness or downside risk based on the provided assumptions. Proceed only with careful review and additional diligence."
    else:
        css_class = "classification-borderline"
        explainer = "The deal has mixed characteristics and requires further diligence before it can be considered attractive."

    st.markdown(
        f"""
        <div class="{css_class}">
            Recommendation Framing: {classification}
            <div class="small-muted" style="margin-top: 0.35rem; font-weight: 400;">
                {explainer}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("This classification is a decision-support signal, not a final investment decision or financial advice.")


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with st.sidebar:
    st.header("About this tool")
    st.write(
        "This app turns rental property assumptions into a structured investment memo. "
        "It combines deterministic calculations with a structured GenAI prompt."
    )
    st.info("The goal is decision support, not automated investment decision-making.")

    st.header("Model Settings")
    model = st.text_input("OpenAI model", value="gpt-4o-mini")
    use_llm = st.checkbox("Generate GenAI memo", value=True)

    st.header("Suggested Demo Case")
    st.caption("Try the default values to show a realistic case with weak near-term rental cash flow.")


st.markdown('<div class="main-title">Residential Rental Deal Memo Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A decision-support tool for evaluating residential rental property fundamentals.</div>', unsafe_allow_html=True)

st.info(
    "This tool creates a structured investment memo to support investor judgment. "
    "It does not replace local market research, inspection findings, financing review, tax advice, or human decision-making."
)

st.divider()
st.subheader("1. Enter Deal Assumptions")

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

col3, col4, col5 = st.columns(3)
with col3:
    vacancy_pct = st.number_input("Vacancy reserve (% of rent)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)
with col4:
    maintenance_pct = st.number_input("Maintenance reserve (% of rent)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)
with col5:
    closing_costs = st.number_input("Estimated closing / initial costs ($)", min_value=0.0, value=10000.0, step=500.0)

st.divider()
generate = st.button("Generate Investment Memo", type="primary", use_container_width=True)

if generate:
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

    st.subheader("2. Investment Snapshot")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Monthly Cash Flow", format_currency(metrics["monthly_cash_flow"]))
    with m2:
        metric_card("Annual Cash Flow", format_currency(metrics["annual_cash_flow"]))
    with m3:
        metric_card("Cap Rate", format_percent(metrics["cap_rate"]))
    with m4:
        metric_card("Cash-on-Cash Return", format_percent(metrics["cash_on_cash_return"]))

    st.caption("Metrics use simplified assumptions and are intended for screening-level analysis only.")

    with st.expander("Show detailed calculations"):
        detail_cols = st.columns(2)
        details = [
            ("Purchase Price", format_currency(metrics["purchase_price"])),
            ("Monthly Rent", format_currency(metrics["monthly_rent"])),
            ("Down Payment", format_currency(metrics["down_payment"])),
            ("Loan Amount", format_currency(metrics["loan_amount"])),
            ("Monthly Mortgage Payment", format_currency(metrics["monthly_mortgage_payment"])),
            ("Monthly Taxes", format_currency(metrics["monthly_taxes"])),
            ("Monthly Insurance", format_currency(metrics["monthly_insurance"])),
            ("Monthly HOA", format_currency(metrics["monthly_hoa"])),
            ("Monthly Vacancy Reserve", format_currency(metrics["monthly_vacancy"])),
            ("Monthly Maintenance Reserve", format_currency(metrics["monthly_maintenance"])),
            ("Monthly Operating Expenses", format_currency(metrics["monthly_operating_expenses"])),
            ("Total Monthly Cost", format_currency(metrics["total_monthly_cost"])),
            ("Annual NOI Before Debt Service", format_currency(metrics["annual_noi"])),
            ("Total Cash Invested", format_currency(metrics["total_cash_invested"])),
        ]
        for i, (label, value) in enumerate(details):
            with detail_cols[i % 2]:
                st.write(f"**{label}:** {value}")

    st.divider()

    if use_llm:
        st.subheader("3. Structured Investment Memo")
        prompt = build_structured_prompt(metrics)
        with st.spinner("Generating structured memo..."):
            memo = call_llm(prompt, model=model)

        classification = extract_classification(memo, metrics)
        show_classification_banner(classification)
        st.markdown(memo)

        with st.expander("Show structured prompt used by the app"):
            st.text(prompt)
    else:
        st.subheader("3. Recommendation Framing")
        classification = infer_classification_from_metrics(metrics)
        show_classification_banner(classification)
        st.info("GenAI memo generation is turned off. Review calculated metrics above.")

    st.divider()
    st.subheader("4. Human Review Boundaries")
    st.write(
        "Before relying on this analysis, the user should verify local rent comparables, property condition, "
        "financing terms, taxes, insurance, HOA rules, vacancy assumptions, and personal investment goals."
    )
