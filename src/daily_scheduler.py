import time
import schedule
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# 📧 CONFIGURATION — loaded from .env file
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
API_ENDPOINT = "http://127.0.0.1:8000/recommend"

if not all([SENDER_EMAIL, RECEIVER_EMAIL, APP_PASSWORD]):
    raise EnvironmentError("Missing email credentials. Check your .env file.")

# Profile parameters matching your Step 1 and Step 2 canvas rules
USER_PAYLOAD = {
    "user_name": "Navya",
    "age": 31,
    "weight": 63.0,
    "ingredients": "Rice, Eggs, Onions, Tomatoes, Lemon, Oats, Spinach",
    "dietary_restriction": "Vegetarian",
    "health_goal": "Maintenance",
    "target_slot": "all"
}

def format_html_email(plan, metadata):
    """Parses the local JSON payload back into a beautiful HTML email layout."""
    target_cal = metadata.get('target_calories', 'Calculated Baseline')
    
    html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <h2 style="color: #1E3A8A;">🍳 Good Morning, {USER_PAYLOAD['user_name']}!</h2>
        <p>Here is your automated daily diet plan tailored by your local AI engine.</p>
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <strong style="text-transform: uppercase; font-size: 12px; opacity: 0.9;">Daily Target Baseline</strong>
            <div style="font-size: 24px; font-weight: bold; margin-top: 5px;">{target_cal}</div>
        </div>
    """
    
    for slot, title in [("morning", "🌅 Morning Breakfast"), ("afternoon", "☀️ Afternoon Lunch"), ("evening", "🌙 Evening Dinner")]:
        meal = plan.get(slot)
        if meal:
            html += f"""
            <div style="border-left: 4px solid #10B981; background-color: #F9FAFB; padding: 15px; margin-bottom: 15px; border-radius: 4px;">
                <h3 style="margin-top: 0; color: #111827;">{title}: {meal.get('name', 'Healthy Option').title()}</h3>
                <p style="margin: 5px 0;"><strong>Macros:</strong> 🔥 {meal.get('calories', 'N/A')} kcal | 🥩 P: {meal.get('protein', 'N/A')} | 🍞 C: {meal.get('carbs', 'N/A')} | 🥑 F: {meal.get('fats', 'N/A')}</p>
                <p style="margin: 5px 0; font-size: 14px; color: #4B5563;"><strong>Instructions:</strong> {meal.get('preparation', 'Cook core elements thoroughly.')}</p>
            </div>
            """
    
    html += """
        <hr style="border: 0; border-top: 1px solid #E5E7EB; margin-top: 30px;">
        <p style="font-size: 12px; color: #9CA3AF; text-align: center;">NutriChef AI Automated Notification Service Engine • Offline Local Inference Layer</p>
    </body>
    </html>
    """
    return html

def send_daily_diet_email():
    print("⏰ 6:00 AM Trigger Activated! Fetching meal matrix layers...")
    try:
        # 1. Fetch live recommendation compilation from backend server
        response = requests.post(API_ENDPOINT, json=USER_PAYLOAD)
        data = response.json()
        
        if data.get("success"):
            plan = data["full_day_plan"]
            metadata = data["user_metadata"]
            
            # 2. Compile message packages
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🍳 Your NutriChef AI Daily Diet Plan - {USER_PAYLOAD['user_name']}"
            msg["From"] = SENDER_EMAIL
            msg["To"] = RECEIVER_EMAIL
            
            email_content = format_html_email(plan, metadata)
            msg.attach(MIMEText(email_content, "html"))
            
            # 3. Establish secure network link via Google SMTP portal
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(SENDER_EMAIL, APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
            print("✅ Email sent successfully without layout defects!")
        else:
            print("❌ Backend returned success=False while processing scheduler loop.")
            
    except Exception as e:
        print(f"❌ Scheduler execution failed: {str(e)}")

# ⏰ CRON ROUTINE: Schedules execution checkpoint every single day at 6:00 AM
schedule.every().day.at("06:00").do(send_daily_diet_email)

print("🚀 NutriChef AI Daily 6:00 AM Email Scheduler Core is running...")
print("Keep this terminal window running in the background to handle delivery routines.")

# Keep script alive process running persistently
while True:
    schedule.run_pending()
    time.sleep(30)  # Check task stacks every 30 seconds