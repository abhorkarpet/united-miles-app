import streamlit as st

st.set_page_config(
    page_title="United Upgrade Evaluator",     # Title shown on browser tab
    page_icon="✈️",                             # Favicon/icon
    layout="centered",                          # Optional: or "wide"
    initial_sidebar_state="auto"                # Optional
)

# Constants for easier maintenance
MILE_VALUE_LOW = 0.012  # United miles valuation low (1.2 cents)
MILE_VALUE_HIGH = 0.015  # United miles valuation high (1.5 cents)
UA_LOGO_URL = "https://logos-world.net/wp-content/uploads/2020/11/United-Airlines-Logo-700x394.png"
VERSION = "5.4"
UPGRADE_COMFORT_HOURS = 6

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

# Helper functions
def calculate_miles_value(miles):
    """Calculate low and high dollar value of miles"""
    return miles * MILE_VALUE_LOW, miles * MILE_VALUE_HIGH

def format_currency(value):
    """Format a value as USD currency"""
    return f"${value:.2f}"

def validate_inputs(miles, cost):
    """Validate basic inputs"""
    if cost < 0:
        return False, "Cost cannot be negative"
    if miles < 0:
        return False, "Miles cannot be negative"
    return True, ""

# Function to evaluate Award Accelerator (miles + PQP purchases)
def evaluate_accelerator(miles, pqp, cost):
    # Validate inputs
    valid, error_message = validate_inputs(miles, cost)
    if not valid:
        return {"Error": error_message}
    
    # Calculate values
    miles_worth_low, miles_worth_high = calculate_miles_value(miles)
    effective_cost_low = cost - miles_worth_high if pqp else cost
    effective_cost_high = cost - miles_worth_low if pqp else cost
    cost_per_mile = cost / miles if miles > 0 else float('inf')
    
    # Calculate PQP cost values
    if pqp > 0:
        pqp_cost_low = effective_cost_low / pqp
        pqp_cost_high = effective_cost_high / pqp
        
        # Determine verdict based on PQP cost
        if pqp_cost_low < 1.30:
            verdict = "✅ Excellent Deal!"
        elif pqp_cost_low < 1.50:
            verdict = "🟡 Decent Value."
        else:
            verdict = "❌ Not Worth It."
    else:
        pqp_cost_low = pqp_cost_high = None
        # Determine verdict based on cost per mile
        if cost_per_mile < 0.01:  # Less than 1 cent per mile is good
            verdict = "✅ Good Deal!"
        elif cost_per_mile < 0.012:  # Less than our low valuation
            verdict = "🟡 Decent Value."
        else:
            verdict = "❌ Not Worth It."

    return {
        "Miles Worth (Low)": format_currency(miles_worth_low),
        "Miles Worth (High)": format_currency(miles_worth_high),
        "Cost Per Mile": f"{cost_per_mile:.3f} cents" if miles > 0 else "N/A",
        "PQP Cost per Dollar": format_currency(pqp_cost_low) if pqp else None,
        "Verdict": verdict,
        "CPM": cost_per_mile * 100 if miles > 0 else 0
    }


def is_upgrade_not_worth_it(travel_hours, cash_upgrade, full_fare, miles, cash_cost, from_class, to_class, original_full_fare):
    """ Determines if an upgrade is not worth it """
    if travel_hours < UPGRADE_COMFORT_HOURS and from_class == "Economy" and to_class == "Premium Plus":
        return "⚠️ Short flight – upgrade may not be worth it."
    
    if cash_upgrade > 0.8 * full_fare and original_full_fare > 0:
        return "⚠️ Upgrade cost is too close to full fare price."

    if (miles > 0 and cash_cost > 0) and (cash_cost + (miles * 0.012) > full_fare) and full_fare > 0:
        return "⚠️ Miles + Cash upgrade is costing more than a full-fare business class ticket."

    if from_class == "Premium Plus" and to_class == "Business (Polaris)" and travel_hours < 5:
        return "⚠️ Small difference in comfort for this flight length – not worth upgrading."

    return None  # Upgrade is reasonable

def evaluate_relative_upgrade_cost(base_fare, upgrade_cost):
    if base_fare == 0:
        return None
    if upgrade_cost < 0.5 * base_fare:
        return "✅ Upgrade is reasonably priced relative to your original fare."
    elif upgrade_cost < 0.8 * base_fare:
        return "🟡 Upgrade is borderline—consider only for longer flights or big comfort boost."
    else:
        return "❌ Upgrade is expensive compared to your base fare."

# Function to evaluate upgrade options & detect bad deals
def evaluate_upgrade(miles, cash_cost, full_cash_upgrade, full_fare_cost, travel_hours, from_class, to_class):
    # Validate inputs
    valid, error_message = validate_inputs(miles, cash_cost)
    if not valid:
        return {"Error": error_message}
    
    # Skip calculation if no upgrade is selected
    if from_class == to_class:
        return {
            "Warning": "⚠️ You've selected the same cabin class for both options. No upgrade needed.",
            "Verdict": "ℹ️ No upgrade selected"
        }
    
    # Calculate comfort factor (longer flights increase perceived value)
    comfort_factor = 1 + (0.05 * travel_hours)
    
    # Get upgrade multiplier based on cabin classes
    upgrade_multiplier = upgrade_multipliers.get((from_class, to_class), 1.0)

    # Handle missing inputs by making best estimates
    original_full_fare_cost = full_fare_cost
    if full_fare_cost == 0:
        full_fare_cost = max(full_cash_upgrade * 1.5, 1000)  # Estimate based on upgrade cost

    if miles == 0 and cash_cost == 0:
        miles, cash_cost = 0, full_cash_upgrade  # Assume only cash upgrade available

    # Value of miles in cash terms
# Calculate miles value
    miles_worth_low, miles_worth_high = calculate_miles_value(miles)
    total_miles_cash_upgrade_low = cash_cost + miles_worth_low
    total_miles_cash_upgrade_high = cash_cost + miles_worth_high

    # Full Cash Upgrade (No Miles)
    total_cash_upgrade = full_cash_upgrade

    # Apply comfort factor to savings
    savings_low, savings_high = ((full_fare_cost - total_miles_cash_upgrade_high) * comfort_factor * upgrade_multiplier, 
                                 (full_fare_cost - total_miles_cash_upgrade_low) * comfort_factor * upgrade_multiplier)
    if total_cash_upgrade == 0:
        total_cash_upgrade = full_fare_cost
    savings_cash_upgrade = (full_fare_cost - total_cash_upgrade) * comfort_factor * upgrade_multiplier

    # Best Upgrade Method Decision
    if savings_high > savings_cash_upgrade and savings_high > 0:
        best_option = "Miles + Cash"
    elif savings_cash_upgrade > 0:
        best_option = "Cash Upgrade"
    else:
        best_option = "Buy Full Fare Ticket"

    verdict = f"✅ **Best Option:** {best_option}"

    # ❌ Detect When the Upgrade is "Not Worth It"
    warning_message = is_upgrade_not_worth_it(travel_hours,total_cash_upgrade,full_fare_cost, miles, cash_cost, from_class, to_class, original_full_fare_cost)

    return {
        "Miles Worth (Low)": f"${miles_worth_low:.2f}",
        "Miles Worth (High)": f"${miles_worth_high:.2f}",
        "Total Upgrade Cost (Miles + Cash)": f"${total_miles_cash_upgrade_low:.2f} - ${total_miles_cash_upgrade_high:.2f}" if miles > 0 else "N/A",
        "Total Upgrade Cost (Cash-Only)": f"${total_cash_upgrade:.2f}",
        "Full-Fare Business/First Class Price": f"${full_fare_cost:.2f}",
        "Savings (Miles + Cash Upgrade)": f"${savings_low:.2f} - ${savings_high:.2f}" if miles > 0 else "N/A",
        "Savings (Cash-Only Upgrade)": f"${savings_cash_upgrade:.2f}",
        "Best Option": best_option,
        "Verdict": verdict,
        "Warning": warning_message,
        "Comfort Factor": comfort_factor
    }

# Function to evaluate Ticket Purchase (Miles vs. Cash vs. Miles + Cash)
def evaluate_best_option(miles_price, cash_price, miles_plus_cash_miles, miles_plus_cash_cash):
    # Calculate miles values
    miles_cash_value_low, miles_cash_value_high = calculate_miles_value(miles_price)
    mixed_miles_value_low, mixed_miles_value_high = calculate_miles_value(miles_plus_cash_miles)
    
    # Calculate total costs for different options
    total_cost_miles_low = miles_cash_value_low
    total_cost_miles_high = miles_cash_value_high
    total_cost_mixed_low = mixed_miles_value_low + miles_plus_cash_cash
    total_cost_mixed_high = mixed_miles_value_high + miles_plus_cash_cash
    
    # Create dictionary of options for easier comparison
    options = {
        "Cash": cash_price,
        "Miles": total_cost_miles_low,  # Use low estimate for conservative comparison
        "Miles + Cash": total_cost_mixed_low if miles_plus_cash_miles > 0 and miles_plus_cash_cash > 0 else float('inf')
    }
    
    # Find option with lowest cost
    best_option = min(options.items(), key=lambda x: x[1] if x[1] > 0 else float('inf'))[0]
    
    # Determine CPM (cents per mile) for award redemptions
    cpm_miles = (cash_price / miles_price) * 100 if miles_price > 0 else 0
    cpm_miles_plus_cash = ((cash_price - miles_plus_cash_cash) / miles_plus_cash_miles) * 100 if miles_plus_cash_miles > 0 else 0
    
    verdict = f"✅ Best Option: **{best_option}**"
    
    # Add advice based on CPM
    advice = None
    if best_option == "Miles" and cpm_miles > 1.5:
        advice = "🎯 Great redemption value! Above average cents-per-mile."
    elif best_option == "Miles + Cash" and cpm_miles_plus_cash > 1.5:
        advice = "🎯 Good value for your miles in the Miles + Cash option!"

    return {
        "Miles Cash Value (Low)": format_currency(miles_cash_value_low),
        "Miles Cash Value (High)": format_currency(miles_cash_value_high),
        "Total Cost (Miles)": f"{format_currency(total_cost_miles_low)} - {format_currency(total_cost_miles_high)}",
        "Total Cost (Miles + Cash)": f"{format_currency(total_cost_mixed_low)} - {format_currency(total_cost_mixed_high)}",
        "Total Cost (Cash)": format_currency(cash_price),
        "CPM (Miles Option)": f"{cpm_miles:.2f} cents" if miles_price > 0 else "N/A",
        "CPM (Miles + Cash)": f"{cpm_miles_plus_cash:.2f} cents" if miles_plus_cash_miles > 0 else "N/A",
        "Best Option": best_option,
        "Verdict": verdict,
        "Advice": advice,
        "CPM_Miles": cpm_miles,
        "CPM_Mixed": cpm_miles_plus_cash
    }

# Function to evaluate Ticket Purchase (Miles vs. Cash vs. Miles + Cash)
def evaluate_miles_purchase(miles_price, cash_price):
    # Calculate miles values
    miles_cash_value_low, miles_cash_value_high = calculate_miles_value(miles_price)
    
    # Calculate total costs for different options
    total_cost_miles_low = miles_cash_value_low
    total_cost_miles_high = miles_cash_value_high
        
    # Determine CPM (cents per mile) for award redemptions
    cpm_miles = (cash_price / miles_price) * 100 if miles_price > 0 else 0
        
    #verdict = f"✅ Best Option: **{best_option}**"
    
    # Add advice based on CPM
    advice = None
    if cpm_miles < 1.2:
        advice = "🎯 Great redemption value! Above average cents-per-mile."
    
    return {
        "Miles Cash Value (Low)": format_currency(miles_cash_value_low),
        "Miles Cash Value (High)": format_currency(miles_cash_value_high),
        "Total Cost (Miles)": f"{format_currency(total_cost_miles_low)} - {format_currency(total_cost_miles_high)}",
        "Total Cost (Cash)": format_currency(cash_price),
        "CPM (Miles Option)": f"{cpm_miles:.2f} cents" if miles_price > 0 else "N/A",
     #   "Verdict": verdict,
        "Advice": advice,
        "CPM_Miles": cpm_miles,

    }

# Initialize session state if not exists
if 'show_help' not in st.session_state:
    st.session_state.show_help = False

# Streamlit UI with Tabs
st.image(UA_LOGO_URL, width=250)  # Display United Airlines Logo
st.title("United Airlines Deal Evaluator ✈️")
st.markdown("Analyze **Award Accelerators, Upgrade Offers, Ticket Purchases, and Buy Miles Offer** to find the best value.")

# Help toggle
help_col1, help_col2 = st.columns([1, 1 ])
with help_col1:
    show_help = st.checkbox("Show Help", st.session_state.show_help)
    st.session_state.show_help = show_help

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["💺 Upgrade Offer", "🎟️ Ticket Purchase", "🏆 Award Accelerator", "💵 Buy Miles"])


with tab1:
    st.subheader("💺 Evaluate Your Upgrade Offer")
    
    if show_help:
        st.info("""
        This evaluates different upgrade options available on United flights.
        - **Miles + Cash Upgrade**: Using miles plus a cash co-pay
        - **Cash-Only Upgrade**: Paying a fee to upgrade without using miles
        - **Full-Fare Business/First**: Buying the higher cabin outright
        
        The tool calculates which option offers the best value based on your inputs.
        """)

    # User Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        from_class = st.selectbox("Current Cabin Class", cabin_classes, key="upgrade_from")
        miles = st.number_input("Miles for Upgrade (Miles + Cash Option, leave 0 if unknown)", min_value=0, step=1000, key="upgrade_miles")
        full_cash_upgrade = st.number_input("Cash-Only Upgrade Cost ($)", min_value=0.0, step=50.0, key="upgrade_cash_only")

    with col2:
        to_class = st.selectbox("Upgrade To", cabin_classes, index=2, key="upgrade_to")
        cash_cost = st.number_input("Cash Cost for Miles + Cash Upgrade ($, leave 0 if unknown)", min_value=0.0, step=50.0)
        full_fare_cost = st.number_input("Full-Fare Business/First Class Cost ($, leave 0 if unknown)", min_value=0.0, step=100.0)
    base_fare = st.number_input("Base Fare You Paid for Economy/Premium ($, leave 0 if unknown)", min_value=0.0, step=50.0)
    base_fare_miles = st.number_input("Base Miles You Paid for Economy/Premium (leave 0 if unknown)", min_value=0.0, step=50.0)

    if base_fare_miles > 0:
        base_fare_miles_value_low, base_fare_miles_value_high = calculate_miles_value(base_fare_miles)
        base_fare = base_fare + base_fare_miles_value_high

    travel_hours = st.slider("Flight Duration (in hours)", min_value=1, max_value=20, value=5, key="upgrade_duration")    

    if st.button("Evaluate Upgrade Offer"):
        result = evaluate_upgrade(miles, cash_cost, full_cash_upgrade, full_fare_cost, travel_hours, from_class, to_class)
        
        # Check for errors
        if "Error" in result:
            st.error(result["Error"])
        else:
            # Stylized Output Section
            st.markdown("### ✈️ **Upgrade Analysis**")

            # Use Columns for better formatting
            if "Warning" in result and result["Warning"] and "No upgrade selected" in result["Verdict"]:
                st.warning(result["Warning"])
            else:
                # **Accentuation of Verdict**
                st.markdown("### 🔎 **Final Verdict**")
                if "✅" in result["Verdict"]:
                    st.success(result["Verdict"])
                else:
                    st.warning(result["Verdict"])

                #col1, col2 = st.columns(2)

                #with col1:
                st.markdown("##### 💰 **Cost Breakdown**")
                st.markdown(f"**Miles Worth:** {result['Miles Worth (Low)']} - {result['Miles Worth (High)']}", unsafe_allow_html=True)
                st.markdown(f"**Miles + Cash Upgrade Cost:** {result['Total Upgrade Cost (Miles + Cash)']}", unsafe_allow_html=True)
                if full_cash_upgrade != 0:
                    st.markdown(f"**Cash-Only Upgrade Cost:** {result['Total Upgrade Cost (Cash-Only)']}", unsafe_allow_html=True)
                if full_fare_cost != 0:
                    st.markdown(f"**Full-Fare Business Class:** {result['Full-Fare Business/First Class Price']}", unsafe_allow_html=True)
                
                # Evaluate relative upgrade cost (based on cash-only upgrade)
                relative_upgrade_msg = evaluate_relative_upgrade_cost(base_fare, full_cash_upgrade)
                if relative_upgrade_msg:
                    st.markdown("### 💸 **Upgrade Cost vs. Base Fare**")
                    if "✅" in relative_upgrade_msg:
                        st.success(relative_upgrade_msg)
                    elif "❌" in relative_upgrade_msg:
                        st.error(relative_upgrade_msg)
                    else:
                        st.warning(relative_upgrade_msg)

                # **Highlight Warnings in Red**
                if result["Warning"]:
                    st.error(result["Warning"])
                # Add flight duration insight
                comfort_factor = result["Comfort Factor"]
                if travel_hours >= UPGRADE_COMFORT_HOURS:
                    st.info(f"Long flight ({travel_hours}h) increases upgrade value by {(comfort_factor-1)*100:.0f}% in our calculations.")

with tab2:
    st.subheader("Compare Ticket Purchase Options")
    
    if show_help:
        st.info("""
        This tab helps you decide the best way to book your ticket:
        - **Miles Redemption**: Using only award miles
        - **Cash**: Paying the full fare with cash
        - **Miles + Cash**: Using a combination of miles and cash
        
        The tool evaluates which option gives you the best value based on standard mile valuations.
        """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        miles_price = st.number_input("Miles Required for Redemption", min_value=0, step=1000, key="purchase_miles")
        miles_plus_cash_miles = st.number_input("Miles for Miles + Cash", min_value=0, step=1000, key="purchase_mixed_miles")
    
    with col2:
        cash_price = st.number_input("Full Cash Ticket Price ($)", min_value=0.0, step=50.0, key="purchase_cash")
        miles_plus_cash_cash = st.number_input("Cash for Miles + Cash ($)", min_value=0.0, step=50.0, key="purchase_mixed_cash")

    if st.button("Evaluate Best Purchase Option"):
        # Check if we have enough data to make a comparison
        if miles_price == 0 and miles_plus_cash_miles == 0:
            st.warning("Please enter miles required for at least one option.")
        elif cash_price == 0:
            st.warning("Please enter the full cash ticket price for comparison.")
        else:
            result = evaluate_best_option(miles_price, cash_price, miles_plus_cash_miles, miles_plus_cash_cash)
            
            # Stylized Output Section
            st.markdown("### 🎟️ **Ticket Purchase Analysis**")

            # Use Columns for better formatting
            #col1, col2 = st.columns(2)

            #with col1:
            st.markdown("##### 💰 **Cost Comparison**")
            st.markdown(f"**Miles Value:** {result['Miles Cash Value (Low)']} - {result['Miles Cash Value (High)']}")
            st.markdown(f"**Total Cost (Miles Only):** {result['Total Cost (Miles)']}")
            if miles_plus_cash_miles > 0 and miles_plus_cash_cash > 0:
                st.markdown(f"**Total Cost (Miles + Cash):** {result['Total Cost (Miles + Cash)']}")
            st.markdown(f"**Total Cost (Cash):** {result['Total Cost (Cash)']}")

            #with col2:
            st.markdown("##### 📊 **Value Assessment**")
            # Show verdict with appropriate styling
            if "✅" in result["Verdict"]:
                st.success(result["Verdict"])
            else:
                st.warning(result["Verdict"])
            
            #st.markdown(f"**Best Option:** <span style='font-size:24px; font-weight:bold;'>{result['Best Option']}</span>", unsafe_allow_html=True)
            
            # Show CPM for redemption options
            if miles_price > 0:
                cpm_miles = result["CPM_Miles"]
                st.markdown(f"**CPM (Miles Only):** {cpm_miles:.2f} cents per mile")
            
            if miles_plus_cash_miles > 0 and miles_plus_cash_cash > 0:
                cpm_mixed = result["CPM_Mixed"]
                st.markdown(f"**CPM (Miles + Cash):** {cpm_mixed:.2f} cents per mile")
            
            # Additional insights section
            st.markdown("##### 💡 **Redemption Value Insights**")
            
            # Show advice if available
            if "Advice" in result and result["Advice"]:
                st.info(result["Advice"])
            
            # Calculate and show cents per mile assessment
            if miles_price > 0:
                cpm = result["CPM_Miles"]
                if cpm > 2.0:
                    st.success(f"Excellent miles redemption value! You're getting {cpm:.2f} cents per mile with the Miles option (avg. is 1.2-1.5¢)")
                elif cpm > 1.5:
                    st.info(f"Good miles redemption value: {cpm:.2f} cents per mile (above the typical 1.2-1.5¢ range)")
                elif cpm < 1.0:
                    st.warning(f"Below average miles redemption value: {cpm:.2f} cents per mile (below the typical 1.2-1.5¢ range)")
            
            if miles_plus_cash_miles > 0 and miles_plus_cash_cash > 0:
                cpm_mixed = result["CPM_Mixed"]
                if cpm_mixed > 2.0:
                    st.success(f"Excellent value with Miles + Cash option! You're getting {cpm_mixed:.2f} cents per mile (avg. is 1.2-1.5¢)")
                elif cpm_mixed > 1.5:
                    st.info(f"Good value with Miles + Cash option: {cpm_mixed:.2f} cents per mile")
                elif cpm_mixed < 1.0:
                    st.warning(f"Below average value with Miles + Cash option: {cpm_mixed:.2f} cents per mile")

with tab3:
    st.subheader("Evaluate Award Accelerator Deals")
    
    if show_help:
        st.info("""
        **Award Accelerator** allows you to purchase additional miles, sometimes with PQP (Premier Qualifying Points).
        - **Miles Offered**: The number of bonus miles you'll receive
        - **PQP Offered**: Premier Qualifying Points (helps earn elite status)
        - **Total Cost**: What United is charging for this offer
        """)
    
    miles = st.number_input("Miles Offered", min_value=0, step=1000, key="accelerator_miles")
    pqp = st.number_input("PQP Offered (Enter 0 if not included)", min_value=0, step=100, key="accelerator_pqp")
    cost = st.number_input("Total Cost ($)", min_value=0.0, step=50.0, key="accelerator_cost")

    if st.button("Evaluate Award Accelerator"):
        result = evaluate_accelerator(miles, pqp, cost)
        
        # Check for errors
        if "Error" in result:
            st.error(result["Error"])
        else:
            # Stylized Output Section
            st.markdown("### 🏆 **Award Accelerator Analysis**")

            # Use Columns for better formatting
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 💰 **Value Breakdown**")
                st.markdown(f"**Miles Worth:** {result['Miles Worth (Low)']} - {result['Miles Worth (High)']}")
                if miles > 0:
                    st.markdown(f"**Cost Per Mile:** {result['Cost Per Mile']}")
                if pqp > 0:
                    st.markdown(f"**PQP Cost:** {result['PQP Cost per Dollar']}/PQP")

            with col2:
                st.markdown("##### 📊 **Value Assessment**")
                # Show verdict with appropriate styling
                if "✅" in result["Verdict"]:
                    st.success(result["Verdict"])
                elif "❌" in result["Verdict"]:
                    st.error(result["Verdict"])
                else:
                    st.warning(result["Verdict"])
                
                # Show bonus advice for CPM
                if miles > 0 and cost > 0:
                    cpm = result["CPM"]
                    if cpm < 1.0:
                        st.success(f"You're paying only {cpm:.3f} cents per mile. This is below the typical valuation of 1.2-1.5 cents each.")
                    elif cpm < 1.2:
                        st.info(f"You're paying {cpm:.3f} cents per mile. This is slightly below the typical valuation of 1.2-1.5 cents each.")
                    else:
                        st.warning(f"You're paying {cpm:.3f} cents per mile. This is above the typical valuation of 1.2-1.5 cents each.")
            
            # Additional insights section
            st.markdown("##### 💡 **Additional Insights**")
            if pqp > 0:
                ratio = pqp / cost
                if ratio > 0.65:
                    st.success(f"This offer provides excellent PQP earning rate ({ratio:.2f} PQP per dollar).")
                elif ratio > 0.5:
                    st.info(f"This offer provides decent PQP earning rate ({ratio:.2f} PQP per dollar).")
                else:
                    st.warning(f"This offer provides below-average PQP earning rate ({ratio:.2f} PQP per dollar).")
            else:
                if miles > 0 and cost > 0:
                    st.info("This offer doesn't include PQP, so it only helps with award travel, not elite status progress.")

with tab4:
    st.subheader("Miles Purchase Deal")
    
    if show_help:
        st.info("""
        This tab helps you decide whether **Miles Offer** is worth it.
        """)
    
    col1, col2 = st.columns(2)

    with col1:
        cash_price = st.number_input("Purchase Price ($)", min_value=0.0, step=50.0, key="purchase_price")

    with col2:
        miles_price = st.number_input("Miles", min_value=0, step=1000, key="purchase_miles_offer")
        bonus_miles = st.number_input("Bonus Miles (if any)", min_value=0, step=1000, key="purchase_miles_bonus_offer")
        
    if st.button("Evaluate The offer"):
        # Check if we have enough data to make a comparison
        if miles_price == 0:
            st.warning("Please enter miles.")
        elif cash_price == 0:
            st.warning("Please enter the purchase price.")
        else:
            result = evaluate_miles_purchase(miles_price + bonus_miles, cash_price)
            
            # Stylized Output Section
            st.markdown("### 🎟️ **Miles Purchase Analysis**")

            # Use Columns for better formatting
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("##### 💰 **Cost Comparison**")
                st.markdown(f"**Miles Value:** {result['Miles Cash Value (Low)']} - {result['Miles Cash Value (High)']}")
                st.markdown(f"**Total Cost (Cash):** {result['Total Cost (Cash)']}")

            with col2:
                st.markdown("##### 📊 **Value Assessment**")
            # Show verdict with appropriate styling
            # if "✅" in result["Verdict"]:
            #     st.success(result["Verdict"])
            # else:
            #     st.warning(result["Verdict"])
            
            #st.markdown(f"**Best Option:** <span style='font-size:24px; font-weight:bold;'>{result['Best Option']}</span>", unsafe_allow_html=True)
            
                # Show CPM for redemption options
                if miles_price > 0:
                    cpm_miles = result["CPM_Miles"]
                    st.markdown(f"**CPM (Miles Only):** {cpm_miles:.2f} cents per mile")
            
            # Additional insights section
            st.markdown("##### 💡 **Redemption Value Insights**")
            
            # Show advice if available
            if "Advice" in result and result["Advice"]:
                st.info(result["Advice"])
            
            # Calculate and show cents per mile assessment
            if miles_price > 0:
                cpm = result["CPM_Miles"]
                if cpm < 1.0:
                    st.success(f"Excellent miles redemption value! You're getting {cpm:.2f} cents per mile with the Miles option (avg. is 1.2-1.5¢)")
                elif cpm < 1.5:
                    st.info(f"Good miles redemption value: {cpm:.2f} cents per mile (below the typical 1.2-1.5¢ range)")
                elif cpm > 1.5:
                    st.warning(f"Below average miles redemption value: {cpm:.2f} cents per mile (above the typical 1.2-1.5¢ range)")

# Add an expanded disclaimer and about section
with st.expander("About & Disclaimer"):
    st.write("This app helps United Airlines travelers evaluate different deals and options to maximize value.")
    st.write("DISCLAIMER: This app is developed for informational purposes only. Please use your own judgment.")
    st.write(f"Version {VERSION}")
    
    st.markdown("""
    ### Miles Valuation
    - This app values United miles at 1.2-1.5 cents each
    - Individual valuations may vary based on your redemption patterns
    - Premium cabin international redemptions often yield higher value
    
    ### Premier Status Considerations (where applicable)
    - Higher status levels may access better upgrade availability
    - PQP requirements vary by status level
    """)