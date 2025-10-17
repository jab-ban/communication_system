import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
import requests
import os
from dotenv import load_dotenv

# ---------- 0. Load Environment Variables ----------
load_dotenv()

class EvolutionAPI:
    BASE_URL = os.getenv("EVO_BASE_URL")
    INSTANCE_NAME = os.getenv("EVO_INSTANCE_NAME")

    def __init__(self):
        self.__api_key = os.getenv("AUTHENTICATION_API_KEY")
        self.__headers = {'apikey': self.__api_key, 'Content-Type': 'application/json'}

    def send_message(self, number, text):
        payload = {'number': number, 'text': text}
        response = requests.post(
            url=f'{self.BASE_URL}/message/sendText/{self.INSTANCE_NAME}',
            headers=self.__headers,
            json=payload
        )
        return response.json()


# ---------- 1. Streamlit Page Config & Style ----------
st.set_page_config(page_title="📧 Email / WhatsApp Sender", page_icon="📨", layout="centered")

st.markdown("""
    <style>
        .main { background-color: #f9f9fb; padding: 2rem; border-radius: 15px; }
        h1 { color: #4B8BBE; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
        .stButton > button { background-color: #4B8BBE; color: white; border-radius: 10px; font-weight: bold; padding: 0.6rem 1.2rem; transition: 0.3s; }
        .stButton > button:hover { background-color: #357ABD; }
    </style>
""", unsafe_allow_html=True)

st.title("📨 Email / WhatsApp Sender App")
st.markdown("### Send messages using multiple accounts — locally loaded data!")
st.markdown("---")


# ---------- 2. Load Local CSV Data ----------
try:
    receivers_df = pd.read_csv('C:/Users/Ban/OneDrive/Desktop/communication sys/emails.csv')
    senders_df = pd.read_csv('C:/Users/Ban/OneDrive/Desktop/communication sys/senders-emails.csv')
    st.success(f"✅ Receivers loaded: **{len(receivers_df)}** | Senders loaded: **{len(senders_df)}**")
except Exception as e:
    st.error(f"❌ Error loading local CSV files: {e}")
    st.stop()


# ---------- 3. Sending Method ----------
method = st.selectbox("📤 Choose Sending Method", ["Email", "WhatsApp"])
delay = 2  # Hidden delay variable for internal use


# ---------- 4. Message Input ----------
if method == "Email":
    subject = st.text_input("📌 Email Subject", "Test Email")
    body_template = st.text_area("💌 Email Body", "Hello {name},\nThis is a test email from my project!")
else:
    subject = None
    body_template = st.text_area("💬 WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")


# ---------- 5. Department Filter ----------
if "dept" in receivers_df.columns:
    departments = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected_depts = st.multiselect("🏢 Choose Department(s)", options=departments, default=departments)

    if not selected_depts:
        st.warning("⚠️ No department selected, sending to all.")
        filtered_df = receivers_df
    else:
        filtered_df = receivers_df[receivers_df["dept"].isin(selected_depts)]
        st.info(f"📋 {len(filtered_df)} receiver(s) found in selected department(s).")
else:
    st.info("ℹ️ No 'dept' column found, sending to all receivers.")
    filtered_df = receivers_df


# ---------- 6. WhatsApp Numbers Check ----------
if method == "WhatsApp":
    if "number" not in filtered_df.columns:
        st.error("❌ 'number' column not found in receivers CSV!")
        st.stop()
    whatsapp_numbers = filtered_df["number"].tolist()


# ---------- 7. Ready to Send ----------
st.markdown("---")
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages Now"):
    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))

    for index, row in filtered_df.iterrows():
        name = row["name"]
        sender_data = next(senders_cycle)
        sender_email = sender_data["email"]
        app_password = sender_data["app_password"]
        message = body_template.format(name=name)

        try:
            if method == "Email":
                receiver = row["email"]
                msg = MIMEText(message)
                msg["Subject"] = subject
                msg["From"] = sender_email
                msg["To"] = receiver

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()
                st.success(f"✅ Email sent to {receiver} from {sender_email}")

            else:  # WhatsApp
                number = str(row["number"])
                api = EvolutionAPI()
                api.send_message(number, message)
                st.success(f"✅ WhatsApp message sent to {number}")

            sent_count += 1

        except Exception as e:
            st.error(f"❌ Failed for {name}: {e}")

        time.sleep(delay)

    st.success(f"🎉 All done! {sent_count}/{total} messages sent successfully.")
