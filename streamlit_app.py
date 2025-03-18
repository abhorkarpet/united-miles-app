import streamlit as st

# United Airlines logo URL
UA_LOGO_URL = "https://logos-world.net/wp-content/uploads/2020/11/United-Airlines-Logo-700x394.png"

# Function to evaluate Award Accelerator (miles + PQP purchases)
def evaluate_accelerator(miles, pqp, cost):
    mile_value_low, mile_value_high = 0.012, 0.015
    miles_worth_low, miles_worth_high = miles * mile_value_low, miles * mile_value_high
    effective_cost_low, effective_cost_high = cost - miles_worth_high if pqp else cost, cost - miles_worth_low if pqp else cost
    cost_per_mile = cost / miles if miles else float('inf')
    pqp_cost_low, pqp_cost_high = (effective_cost_low / pqp if pqp else None), (effective_cost_high / pqp if pqp else None)

    verdict = "✅ Excellent Deal!" if (pqp_cost_low and pqp_cost_low < 1.30) else "🟡 Decent Value." if (pqp_cost_low and pqp_cost_low < 1.50) else "❌ Not Worth It."

    return {
        "Miles Worth (Low)": f"${miles_worth_low:.2f}",
        "Miles Worth (High)": f"${miles_worth_high:.2f}",
        "PQP Cost per Dollar": f"${pqp_cost_low:.2f}" if pqp else None,
        "Verdict": verdict
    }

# Function to evaluate Upgrade Offer (miles + cash vs. full fare)
def evaluate_upgrade(miles, cash_cost, full_fare_cost):
    mile_value_low, mile_value_high = 0.012, 0.015
    miles_worth_low, miles_worth_high = miles * mile_value_low, miles * mile_value_high
    total_upgrade_cost_low, total_upgrade_cost_high = cash_cost + miles_worth_low, cash_cost + miles_worth_high
    savings_low, savings_high = full_fare_cost - total_upgrade_cost_high, full_fare_cost - total_upgrade_cost_low

    verdict = "✅ Good Upgrade Deal!" if savings_high > 0.3 * full_fare_cost else "❌ Not Worth It."

    return {
        "Miles Worth (Low)": f"${miles_worth_low:.2f}",
        "Miles Worth (High)": f"${miles_worth_high:.2f}",
        "Total Upgrade Cost": f"${total_upgrade_cost_low:.2f} - ${total_upgrade_cost_high:.2f}",
        "Savings Compared to Full Fare": f"${savings_low:.2f} - ${savings_high:.2f}",
        "Verdict": verdict
    }

# Function to evaluate Ticket Purchase (Miles vs. Cash vs. Miles + Cash)
def evaluate_best_option(miles_price, cash_price, miles_plus_cash_miles, miles_plus_cash_cash):
    mile_value_low, mile_value_high = 0.012, 0.015
    miles_cash_value_low, miles_cash_value_high = miles_price * mile_value_low, miles_price * mile_value_high
    mixed_miles_value_low, mixed_miles_value_high = miles_plus_cash_miles * mile_value_low, miles_plus_cash_miles * mile_value_high

    total_cost_miles_low, total_cost_miles_high = miles_cash_value_low, miles_cash_value_high
    total_cost_mixed_low, total_cost_mixed_high = mixed_miles_value_low + miles_plus_cash_cash, mixed_miles_value_high + miles_plus_cash_cash

    best_option = "Cash" if cash_price < total_cost_miles_low and cash_price < total_cost_mixed_low else (
        "Miles" if total_cost_miles_low < cash_price and total_cost_miles_low < total_cost_mixed_low else "Miles + Cash"
    )

    verdict = f"✅ Best Option: **{best_option}**"

    return {
        "Miles Cash Value (Low)": f"${miles_cash_value_low:.2f}",
        "Miles Cash Value (High)": f"${miles_cash_value_high:.2f}",
        "Total Cost (Miles)": f"${total_cost_miles_low:.2f} - ${total_cost_miles_high:.2f}",
        "Total Cost (Miles + Cash)": f"${total_cost_mixed_low:.2f} - ${total_cost_mixed_high:.2f}",
        "Best Option": best_option,
        "Verdict": verdict
    }

# Streamlit UI with Tabs
st.image(UA_LOGO_URL, width=250)  # Display United Airlines Logo
st.title("United Airlines Deal Evaluator ✈️")
st.markdown("Analyze **Award Accelerators, Upgrade Offers, and Ticket Purchases** to find the best value.")

tab1, tab2, tab3 = st.tabs(["🏆 Award Accelerator", "💺 Upgrade Offer", "🎟️ Ticket Purchase"])

with tab1:
    st.subheader("Evaluate Award Accelerator Deals")
    miles = st.number_input("Miles Offered", min_value=0, step=1000)
    pqp = st.number_input("PQP Offered (Enter 0 if not included)", min_value=0, step=100)
    cost = st.number_input("Total Cost ($)", min_value=0.0, step=50.0)

    if st.button("Evaluate Award Accelerator"):
        result = evaluate_accelerator(miles, pqp, cost)
        for key, value in result.items():
            if value:
                st.metric(key, value)
        st.success(result["Verdict"]) if "✅" in result["Verdict"] else st.warning(result["Verdict"]) if "🟡" in result["Verdict"] else st.error(result["Verdict"])

with tab2:
    st.subheader("Evaluate Upgrade Offer")
    miles = st.number_input("Miles Required", min_value=0, step=1000)
    cash_cost = st.number_input("Cash Cost of Upgrade ($)", min_value=0.0, step=50.0)
    full_fare_cost = st.number_input("Full-Fare Business/First Class Cost ($)", min_value=0.0, step=100.0)

    if st.button("Evaluate Upgrade Offer"):
        result = evaluate_upgrade(miles, cash_cost, full_fare_cost)
        for key, value in result.items():
            if value:
                st.metric(key, value)
        st.success(result["Verdict"]) if "✅" in result["Verdict"] else st.error(result["Verdict"])

with tab3:
    st.subheader("Compare Ticket Purchase Options")
    miles_price = st.number_input("Miles Required for Redemption", min_value=0, step=1000)
    cash_price = st.number_input("Full Cash Ticket Price ($)", min_value=0.0, step=50.0)
    miles_plus_cash_miles = st.number_input("Miles for Miles + Cash", min_value=0, step=1000)
    miles_plus_cash_cash = st.number_input("Cash for Miles + Cash ($)", min_value=0.0, step=50.0)

    if st.button("Evaluate Best Purchase Option"):
        result = evaluate_best_option(miles_price, cash_price, miles_plus_cash_miles, miles_plus_cash_cash)
        for key, value in result.items():
            if value:
                st.metric(key, value)
        st.success(result["Verdict"])
