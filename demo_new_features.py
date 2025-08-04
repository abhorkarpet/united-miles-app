#!/usr/bin/env python3
"""
Demo script for the new Elite Status Tracker and Personal Value Calculator features
"""

# Import the functions from the main app
import sys
sys.path.append('.')

# Mock the constants and functions that would normally come from streamlit_app.py
ELITE_STATUS_THRESHOLDS = {
    "General Member": {"pqp": 0, "pqf": 0},
    "Premier Silver": {"pqp": 4000, "pqf": 25},
    "Premier Gold": {"pqp": 8000, "pqf": 50},
    "Premier Platinum": {"pqp": 12000, "pqf": 75},
    "Premier 1K": {"pqp": 18000, "pqf": 100},
}

DEFAULT_TRAVEL_PATTERNS = {
    "business_traveler": {
        "annual_flights": 40,
        "avg_flight_hours": 3.5,
        "domestic_international_ratio": 0.7,
        "upgrade_value_multiplier": 1.3,
        "mile_valuation": 0.014
    },
    "leisure_traveler": {
        "annual_flights": 8,
        "avg_flight_hours": 6.0,
        "domestic_international_ratio": 0.3,
        "upgrade_value_multiplier": 1.1,
        "mile_valuation": 0.013
    },
    "frequent_flyer": {
        "annual_flights": 60,
        "avg_flight_hours": 4.0,
        "domestic_international_ratio": 0.5,
        "upgrade_value_multiplier": 1.5,
        "mile_valuation": 0.015
    }
}

def get_current_status(pqp, pqf):
    """Determine current elite status based on PQP and PQF"""
    current_status = "General Member"
    for status, requirements in ELITE_STATUS_THRESHOLDS.items():
        if pqp >= requirements["pqp"] and pqf >= requirements["pqf"]:
            current_status = status
    return current_status

def get_next_status(current_status):
    """Get the next elite status level"""
    statuses = list(ELITE_STATUS_THRESHOLDS.keys())
    current_index = statuses.index(current_status)
    if current_index < len(statuses) - 1:
        return statuses[current_index + 1]
    return current_status

def calculate_status_progress(current_pqp, current_pqf, purchase_pqp=0):
    """Calculate progress toward next status level"""
    current_status = get_current_status(current_pqp, current_pqf)
    next_status = get_next_status(current_status)
    
    if current_status == next_status:
        return {
            "current_status": current_status,
            "next_status": "Max Level Reached",
            "pqp_needed": 0,
            "pqf_needed": 0,
            "progress_percentage": 100,
            "will_purchase_help": False
        }
    
    next_requirements = ELITE_STATUS_THRESHOLDS[next_status]
    pqp_needed = max(0, next_requirements["pqp"] - current_pqp)
    pqf_needed = max(0, next_requirements["pqf"] - current_pqf)
    
    # Calculate progress percentage based on PQP
    if next_requirements["pqp"] > 0:
        progress_percentage = min(100, (current_pqp / next_requirements["pqp"]) * 100)
    else:
        progress_percentage = 100
    
    # Check if purchase will help achieve next status
    pqp_after_purchase = current_pqp + purchase_pqp
    will_purchase_help = pqp_after_purchase >= next_requirements["pqp"] and current_pqf >= next_requirements["pqf"]
    
    return {
        "current_status": current_status,
        "next_status": next_status,
        "pqp_needed": pqp_needed,
        "pqf_needed": pqf_needed,
        "progress_percentage": progress_percentage,
        "will_purchase_help": will_purchase_help,
        "pqp_after_purchase": pqp_after_purchase
    }

def get_personalized_mile_value(travel_pattern, redemption_preferences):
    """Calculate personalized mile valuation based on travel patterns"""
    base_value = DEFAULT_TRAVEL_PATTERNS[travel_pattern]["mile_valuation"]
    
    adjustments = {
        "economy_domestic": -0.002,
        "economy_international": 0.0,
        "business_domestic": 0.001,
        "business_international": 0.003,
        "first_international": 0.005
    }
    
    return base_value + adjustments.get(redemption_preferences, 0)

def demo_elite_status_tracker():
    """Demo the Elite Status Tracker functionality"""
    print("🏅 Elite Status Tracker Demo")
    print("=" * 50)
    
    # Example scenarios
    scenarios = [
        {"name": "New Member", "pqp": 1500, "pqf": 8, "purchase_pqp": 2000},
        {"name": "Close to Silver", "pqp": 3500, "pqf": 20, "purchase_pqp": 800},
        {"name": "Gold Member", "pqp": 9500, "pqf": 55, "purchase_pqp": 1500},
        {"name": "Platinum Chase", "pqp": 10500, "pqf": 65, "purchase_pqp": 2000},
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   Current: {scenario['pqp']} PQP, {scenario['pqf']} PQF")
        print(f"   Purchase: {scenario['purchase_pqp']} PQP")
        
        progress = calculate_status_progress(
            scenario['pqp'], 
            scenario['pqf'], 
            scenario['purchase_pqp']
        )
        
        print(f"   Status: {progress['current_status']} → {progress['next_status']}")
        print(f"   Progress: {progress['progress_percentage']:.1f}%")
        print(f"   Still need: {progress['pqp_needed']} PQP, {progress['pqf_needed']} PQF")
        
        if progress['will_purchase_help']:
            print(f"   ✅ This purchase will achieve {progress['next_status']}!")
        else:
            remaining = max(0, progress['pqp_needed'] - scenario['purchase_pqp'])
            print(f"   ⏳ After purchase, still need {remaining} PQP")

def demo_personal_value_calculator():
    """Demo the Personal Value Calculator functionality"""
    print("\n\n👤 Personal Value Calculator Demo")
    print("=" * 50)
    
    # Example traveler profiles
    profiles = [
        {
            "name": "Business Traveler",
            "pattern": "business_traveler",
            "redemption": "business_domestic"
        },
        {
            "name": "Leisure Traveler", 
            "pattern": "leisure_traveler",
            "redemption": "economy_international"
        },
        {
            "name": "Frequent Flyer",
            "pattern": "frequent_flyer", 
            "redemption": "business_international"
        }
    ]
    
    for profile in profiles:
        print(f"\n✈️ Profile: {profile['name']}")
        
        pattern_data = DEFAULT_TRAVEL_PATTERNS[profile['pattern']]
        personal_value = get_personalized_mile_value(profile['pattern'], profile['redemption'])
        
        print(f"   Travel Pattern: {profile['pattern'].replace('_', ' ').title()}")
        print(f"   Annual Flights: {pattern_data['annual_flights']}")
        print(f"   Avg Flight Hours: {pattern_data['avg_flight_hours']}")
        print(f"   Personal Mile Value: {personal_value:.3f} cents")
        print(f"   Upgrade Multiplier: {pattern_data['upgrade_value_multiplier']}")
        
        # Example purchase analysis
        miles_cost = 2.5  # cents per mile
        if miles_cost < personal_value * 100:
            print(f"   💳 Mile purchase at {miles_cost}¢ is GOOD for this profile")
        else:
            print(f"   💳 Mile purchase at {miles_cost}¢ is EXPENSIVE for this profile")

def demo_integration_example():
    """Demo how the features work together"""
    print("\n\n🔗 Integration Example")
    print("=" * 50)
    
    # Traveler considering a status run
    current_pqp = 3200
    current_pqf = 18
    potential_purchase_pqp = 1200
    travel_pattern = "business_traveler"
    
    print("📋 Scenario: Business traveler considering a status run purchase")
    print(f"   Current: {current_pqp} PQP, {current_pqf} PQF")
    print(f"   Considering purchase worth: {potential_purchase_pqp} PQP")
    
    # Check status progress
    progress = calculate_status_progress(current_pqp, current_pqf, potential_purchase_pqp)
    print(f"\n🎯 Status Analysis:")
    print(f"   Current Status: {progress['current_status']}")
    print(f"   Next Status: {progress['next_status']}")
    print(f"   Will purchase help reach next level? {'Yes' if progress['will_purchase_help'] else 'No'}")
    
    # Get personal mile valuation
    personal_value = get_personalized_mile_value(travel_pattern, "business_domestic")
    print(f"\n💰 Personal Value Analysis:")
    print(f"   Personal mile value: {personal_value:.3f} cents")
    print(f"   Standard range: 1.2-1.5 cents")
    
    # Recommendation
    if progress['will_purchase_help'] and personal_value >= 0.013:
        print(f"\n✅ RECOMMENDATION: This looks like a good status run opportunity!")
        print(f"   - Achieves {progress['next_status']} status")
        print(f"   - Aligns with your {personal_value:.3f}¢ mile valuation")
    else:
        print(f"\n⚠️ RECOMMENDATION: Consider carefully")
        if not progress['will_purchase_help']:
            print(f"   - Won't achieve next status level")
        if personal_value < 0.013:
            print(f"   - Below your personal mile valuation")

if __name__ == "__main__":
    print("🎉 United Airlines Elite Status & Personal Value Calculator Demo")
    print("=" * 70)
    
    demo_elite_status_tracker()
    demo_personal_value_calculator()
    demo_integration_example()
    
    print("\n\n📱 To use these features:")
    print("1. Run: streamlit run streamlit_app.py")
    print("2. Navigate to the '🏅 Elite Status Tracker' tab")
    print("3. Navigate to the '👤 Personal Calculator' tab")
    print("4. Use your personalized settings across all tabs!")