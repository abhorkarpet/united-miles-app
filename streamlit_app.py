import streamlit as st

# Function to calculate award accelerator value
def evaluate_accelerator(miles, pqp, cost):
    # United miles estimated value (range)
    mile_value_low = 0.012  # 1.2 cents per mile
    mile_value_high = 0.015  # 1.5 cents per mile

    # Calculate miles' worth
    miles_worth_low = miles * mile_value_low
    miles_worth_high = miles * mile_value_high

    # Calculate effective cost after miles valuation
    effective_cost_low = cost - miles_worth_high
    effective_cost_high = cost - miles_worth_low

    # Calculate cost per PQP
    pqp_cost_low = effective_cost_low / pqp if pqp else 0
    pqp_cost_high = effective_cost_high / pqp if pqp else 0

    # Evaluation criteria
    is_good_pqp = pqp_cost_low < 1.50  # Below $1.50 per PQP is decent
    is_great_pqp = pqp_cost_low < 1.30  # Below $1.30 per PQP is excellent
    is_miles_worth_it = miles_worth_high >= (cost * 0.15)  # At least 15% of cost in miles value

    # Generate recommendation
    if is_great_pqp and is_miles_worth_it:
        verdict = "✅ Excellent Deal! Worth it if you need PQP for status."
    elif is_good_pqp:
        verdict = "🟡 Decent Deal. If you need PQP to hit status, this could be good."
    else:
        verdict = "❌ Not Worth It. Consider earning PQP through flights or a United credit card."

    return {
        "Miles Worth (Low)": f"${miles_worth_low:.2f}",
        "Miles Worth (High)": f"${miles_worth_high:.2f}",
        "Effective Cost After Miles Value (Low)": f"${effective_cost_low:.2f}",
        "Effective Cost After Miles Value (High)": f"${effective_cost_high:.2f}",
        "PQP Cost per Dollar (Low)": f"${pqp_cost_low:.2f}",
        "PQP Cost per Dollar (High)": f"${pqp_cost_high:.2f}",
        "Verdict": verdict
    }

# Streamlit UI
st.title("United Airlines Award Accelerator Evaluator ✈️")

st.markdown("Enter the details of your United Award Accelerator offer to see if it's worth it.")

# User inputs
miles = st.number_input("Miles Offered", min_value=0, step=1000)
pqp = st.number_input("PQP Offered", min_value=0, step=100)
cost = st.number_input("Total Cost of Offer ($)", min_value=0.0, step=50.0, format="%.2f")

# Evaluate button
if st.button("Evaluate Offer"):
    if miles == 0 and pqp == 0:
        st.error("Enter at least miles or PQP to evaluate.")
    else:
        result = evaluate_accelerator(miles, pqp, cost)
        st.subheader("Evaluation Results")
        for key, value in result.items():
            st.write(f"**{key}:** {value}")
