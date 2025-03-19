import streamlit as st

# United Airlines logo URL
UA_LOGO_URL = "https://logos-world.net/wp-content/uploads/2020/11/United-Airlines-Logo-700x394.png"
VERSION = "2.1"

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


# Cabin Class Options
cabin_classes = ["Economy", "Premium Plus", "Business (Polaris)"]

# Upgrade Value Multipliers
upgrade_multipliers = {
    ("Economy", "Premium Plus"): 1.2,
    ("Economy", "Business (Polaris)"): 1.5,
    ("Premium Plus", "Business (Polaris)"): 1.3,
    ("Business (Polaris)", "Business (Polaris)"): 1.0,  # No upgrade
    ("Economy", "Economy"): 1.0,  # No upgrade
    ("Premium Plus", "Premium Plus"): 1.0,  # No upgrade
}

# Function to evaluate upgrade options & detect bad deals
def evaluate_upgrade(miles, cash_cost, full_cash_upgrade, full_fare_cost, travel_hours, from_class, to_class):
    mile_value_low, mile_value_high = 0.012, 0.015  # United miles valuation (1.2-1.5 cents)
    comfort_factor = 1 + (0.05 * travel_hours)  # Longer flights increase perceived value
    upgrade_multiplier = upgrade_multipliers.get((from_class, to_class), 1.0)

    # Value of miles in cash terms
    miles_worth_low, miles_worth_high = miles * mile_value_low, miles * mile_value_high
    total_miles_cash_upgrade_low = cash_cost + miles_worth_low
    total_miles_cash_upgrade_high = cash_cost + miles_worth_high

    # Full Cash Upgrade (No Miles)
    total_cash_upgrade = full_cash_upgrade

    # Full Fare Purchase
    adjusted_full_fare = full_fare_cost

    # Apply comfort & upgrade multiplier to savings
    savings_low, savings_high = ((adjusted_full_fare - total_miles_cash_upgrade_high) * comfort_factor * upgrade_multiplier, 
                                 (adjusted_full_fare - total_miles_cash_upgrade_low) * comfort_factor * upgrade_multiplier)
    savings_cash_upgrade = (adjusted_full_fare - total_cash_upgrade) * comfort_factor * upgrade_multiplier

    # Best Upgrade Method Decision
    if savings_high > savings_cash_upgrade and savings_high > 0:
        best_option = "Miles + Cash"
    elif savings_cash_upgrade > 0:
        best_option = "Cash Upgrade"
    else:
        best_option = "Buy Full Fare Ticket"

    verdict = f"✅ Best Option: **{best_option}**"

    # ❌ Detect When the Upgrade is "Not Worth It"
    warning_message = None

    # Small upgrade on a short flight
    if travel_hours < 3 and (from_class, to_class) in [("Economy", "Premium Plus"), ("Premium Plus", "Business (Polaris)")]:
        warning_message = "⚠️ Short flight – upgrade may not be worth it."

    # Upgrade cost too high compared to full fare
    elif total_cash_upgrade > 0.8 * adjusted_full_fare:
        warning_message = "⚠️ Upgrade cost is too close to full fare price."

    # Miles + Cash upgrade is more expensive than outright buying a business ticket
    elif total_miles_cash_upgrade_high > adjusted_full_fare:
        warning_message = "⚠️ Miles + Cash upgrade is costing more than a full-fare business class ticket."

    return {
        "Miles Worth (Low)": f"${miles_worth_low:.2f}",
        "Miles Worth (High)": f"${miles_worth_high:.2f}",
        "Total Upgrade Cost (Miles + Cash)": f"${total_miles_cash_upgrade_low:.2f} - ${total_miles_cash_upgrade_high:.2f}",
        "Total Upgrade Cost (Cash-Only)": f"${total_cash_upgrade:.2f}",
        "Full-Fare Business/First Class Price": f"${adjusted_full_fare:.2f}",
        "Savings (Miles + Cash Upgrade)": f"${savings_low:.2f} - ${savings_high:.2f}",
        "Savings (Cash-Only Upgrade)": f"${savings_cash_upgrade:.2f}",
        "Best Option": best_option,
        "Verdict": verdict,
        "Warning": warning_message  # NEW: Store warning message
    }


# Function to evaluate Ticket Purchase (Miles vs. Cash vs. Miles + Cash)
def evaluate_best_option(miles_price, cash_price, miles_plus_cash_miles, miles_plus_cash_cash):
    mile_value_low, mile_value_high = 0.012, 0.015
    miles_cash_value_low, miles_cash_value_high = miles_price * mile_value_low, miles_price * mile_value_high
    mixed_miles_value_low, mixed_miles_value_high = miles_plus_cash_miles * mile_value_low, miles_plus_cash_miles * mile_value_high

    total_cost_miles_low, total_cost_miles_high = miles_cash_value_low, miles_cash_value_high
    total_cost_mixed_low, total_cost_mixed_high = mixed_miles_value_low + miles_plus_cash_cash, mixed_miles_value_high + miles_plus_cash_cash

    if total_cost_mixed_low > 0:
        best_option = "Cash" if cash_price < total_cost_miles_low and cash_price < total_cost_mixed_low else (
            "Miles" if total_cost_miles_low < cash_price and total_cost_miles_low < total_cost_mixed_low else "Miles + Cash"
        )
    else:
        if cash_price < total_cost_miles_low:
            best_option = "Cash"  
        else:
            if total_cost_miles_low < cash_price:
                best_option = "Miles"

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
        if "✅" in result["Verdict"]:
            st.success(result["Verdict"])
        elif "❌" in result["Verdict"]:
            st.error(result["Verdict"])
        else:
            st.warning(result["Verdict"])


with tab2:
    st.subheader("💺 Evaluate Your Upgrade Offer")

    # User Inputs
    from_class = st.selectbox("Current Cabin Class", cabin_classes)
    to_class = st.selectbox("Upgrade To", cabin_classes, index=2)
    travel_hours = st.number_input("Flight Duration (in hours)", min_value=1, max_value=20, step=1)
    miles = st.number_input("Miles Required for Upgrade (Miles + Cash Option)", min_value=0, step=1000)
    cash_cost = st.number_input("Cash Cost for Miles + Cash Upgrade ($)", min_value=0.0, step=50.0)
    full_cash_upgrade = st.number_input("Cash-Only Upgrade Cost ($)", min_value=0.0, step=50.0)
    full_fare_cost = st.number_input("Full-Fare Business/First Class Cost ($)", min_value=0.0, step=100.0)

    if st.button("Evaluate Upgrade Offer"):
        result = evaluate_upgrade(miles, cash_cost, full_cash_upgrade, full_fare_cost, travel_hours, from_class, to_class)

        # **Stylized Output Section**
        st.markdown("### ✈️ **Upgrade Analysis**")

        # **Use Columns to Format Output for Better Readability**
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 💰 **Cost Breakdown**")
            st.markdown(f"**Miles Worth:** {result['Miles Worth (Low)']} - {result['Miles Worth (High)']}", unsafe_allow_html=True)
            st.markdown(f"**Miles + Cash Upgrade Cost:** {result['Total Upgrade Cost (Miles + Cash)']}", unsafe_allow_html=True)
            st.markdown(f"**Cash-Only Upgrade Cost:** {result['Total Upgrade Cost (Cash-Only)']}", unsafe_allow_html=True)
            st.markdown(f"**Full-Fare Business Class:** {result['Full-Fare Business/First Class Price']}", unsafe_allow_html=True)

        with col2:
            st.markdown("##### 💵 **Savings & Decision**")
            st.markdown(f"**Savings (Miles + Cash Upgrade):** {result['Savings (Miles + Cash Upgrade)']}", unsafe_allow_html=True)
            st.markdown(f"**Savings (Cash-Only Upgrade):** {result['Savings (Cash-Only Upgrade)']}", unsafe_allow_html=True)
            st.markdown(f"**Best Option:** <span style='font-size:24px; font-weight:bold;'>{result['Best Option']}</span>", unsafe_allow_html=True)
        
        if "✅" in result["Verdict"]:
            st.success(result["Verdict"])
        else:
            st.warning(result["Verdict"])

        # **Highlight Warnings in Red**
        if result["Warning"]:
            st.error(result["Warning"])



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
        if "✅" in result["Verdict"]:
            st.success(result["Verdict"]) 
        else:
            st.error(result["Verdict"])

st.write("DISCLAIMER: This app is developed for informational purpose only. Please use your own judgement.")
st.write(f"Version "+VERSION)