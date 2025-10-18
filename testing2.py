import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
import time
from itertools import cycle
import requests
from io import StringIO

# ---------- Page Config ----------
st.set_page_config(
    page_title="📧 Email / WhatsApp Sender",
    page_icon="📨",
    layout="centered"
)

# ---------- Custom CSS ----------
st.markdown("""
    <style>
        .main { background-color: #f9f9fb; padding: 2rem; border-radius: 15px; }
        h1 { color: #4B8BBE; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
        .stButton > button { 
            background-color: #4B8BBE; color: white; border-radius: 10px; 
            font-weight: bold; padding: 0.6rem 1.2rem; transition: 0.3s; 
        }
        .stButton > button:hover { background-color: #357ABD; }
    </style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.title("📨 Email / WhatsApp Sender App")
st.markdown("### Send messages using multiple accounts!")
st.markdown("---")

# ---------- Load CSVs ----------
def load_csv(secret_key):
    """Load CSV from Streamlit Secrets safely"""
    csv_text = st.secrets[secret_key]
    df = pd.read_csv(StringIO(csv_text.strip()))
    return df

receivers_df = load_csv("emails_csv")
senders_df = load_csv("senders_csv")

st.success(f"✅ Receivers loaded: {len(receivers_df)} | Senders loaded: {len(senders_df)}")

# ---------- Sending Method ----------
method = st.selectbox("📤 Choose Sending Method", ["Email", "WhatsApp"])
delay = 2  # seconds

# ---------- Message Fields ----------
if method == "Email":
    subject = st.text_input("📌 Email Subject", "Test Email")
    body_template = st.text_area("💌 Email Body", "Hello {name},\nThis is a test email!")
else:
    subject = None
    body_template = st.text_area("💬 WhatsApp Message", "Hi {name}, this is a WhatsApp message!")

# ---------- Department Filter ----------
if "dept" in receivers_df.columns:
    depts = sorted(receivers_df["dept"].dropna().unique())
    selected_depts = st.multiselect("🏢 Choose Department(s)", options=depts, default=depts)
    filtered_df = receivers_df[receivers_df["dept"].isin(selected_depts)] if selected_depts else receivers_df
else:
    filtered_df = receivers_df

# ---------- WhatsApp numbers check ----------
if method == "WhatsApp" and "number" not in filtered_df.columns:
    st.error("❌ 'number' column not found in receivers file!")
    st.stop()

# ---------- Ready to Send ----------
st.markdown("---")
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages Now"):
    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))

    for _, row in filtered_df.iterrows():
        name = row["name"]
        sender_data = next(senders_cycle)
        sender_email = sender_data.get("email")
        app_password = sender_data.get("app_password")
        message = body_template.format(name=name)

        try:
            if method == "Email":
                receiver = row["email"]
                msg = MIMEText(message)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = receiver

                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, app_password)
                    server.send_message(msg)

                st.success(f"✅ Email sent to {receiver} from {sender_email}")

            else:  # WhatsApp
                number = str(row["number"])
                api_base = st.secrets["EVO_BASE_URL"]
                instance_name = st.secrets["EVO_INSTANCE_NAME"]
                api_key = st.secrets["AUTHENTICATION_API_KEY"]

                headers = {"apikey": api_key, "Content-Type": "application/json"}
                payload = {"number": number, "text": message}
                res = requests.post(f"{api_base}/message/sendText/{instance_name}", headers=headers, json=payload)

                if res.status_code == 200:
                    st.success(f"✅ WhatsApp message sent to {number}")
                else:
                    st.error(f"❌ Failed to send WhatsApp message to {number}: {res.text}")

            sent_count += 1
        except Exception as e:
            st.error(f"❌ Failed for {name}: {e}")

        time.sleep(delay)

    st.success(f"🎉 Done! {sent_count}/{total} messages sent successfully.")
