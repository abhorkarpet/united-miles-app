import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# United Airlines logo
UA_LOGO_URL = "https://logos-world.net/wp-content/uploads/2021/03/United-Airlines-Logo.png"

# Function to send email notification
def send_email_notification(to_email, origin, destination, date, miles_required, cash_price):
    """Sends an email notification when a better redemption option is found"""
    sender_email = "your-email@gmail.com"  # Replace with your email
    sender_password = "your-email-password"  # Replace with your email password

    subject = f"United Award Seat Found for {origin} to {destination}!"
    body = f"""
    A lower redemption award seat has been found for your trip:
    
    🛫 Route: {origin} → {destination}
    📅 Travel Date: {date}
    🎟️ Miles Required: {miles_required} miles
    💰 Cash Price: ${cash_price}
    
    Book now on United's website before it disappears!
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, msg.as_string())
        return "✅ Notification sent!"
    except Exception as e:
        return f"❌ Email error: {str(e)}"

# Function to check real-time award availability (United API)
def check_award_availability(origin, destination, date):
    """Fetches live award availability from United (requires API key)"""
    try:
        API_URL = f"https://api.united.com/award-search?origin={origin}&destination={destination}&date={date}"
        headers = {"Authorization": "Bearer YOUR_API_KEY"}  # Replace with actual API Key
        response = requests.get(API_URL, headers=headers)

        if response.status_code == 200:
            data = response.json()
            award_miles = data.get("lowest_miles", "N/A")
            cash_price = data.get("cash_price", "N/A")
            return award_miles, cash_price
        else:
            return None, f"Error: {response.status_code}"
    except Exception as e:
        return None, f"API Error: {str(e)}"

# Streamlit UI with Tabs
st.image(UA_LOGO_URL, width=250)  # Display United Airlines Logo
st.title("United Airlines Deal Evaluator ✈️")
st.markdown("Analyze **Award Accelerators, Upgrade Offers, and Ticket Purchases** to find the best value.")

# Real-Time Award Search with Notifications
st.subheader("🔍 Check Real-Time Award Availability")
origin = st.text_input("Departure Airport (e.g., SFO)")
destination = st.text_input("Arrival Airport (e.g., JFK)")
date = st.date_input("Travel Date")

send_email = st.checkbox("📩 Enable Email Notifications for Lower Award Seats")
email_address = st.text_input("Enter your email for alerts") if send_email else None

if st.button("Check Availability"):
    if origin and destination and date:
        award_miles, cash_price = check_award_availability(origin, destination, date.strftime("%Y-%m-%d"))

        if award_miles and cash_price:
            st.write(f"🎟️ **Award Seat Available:** {award_miles} miles")
            st.write(f"💰 **Cash Price:** ${cash_price}")

            if send_email and email_address:
                email_result = send_email_notification(email_address, origin, destination, date, award_miles, cash_price)
                st.write(email_result)
        else:
            st.error("No award seats found or an API issue occurred.")
    else:
        st.error("Please enter valid origin, destination, and date.")
