import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
import requests
import os
from dotenv import load_dotenv

# ---------- Load environment variables ----------
load_dotenv()

EVO_BASE_URL = os.getenv("EVO_BASE_URL")
EVO_INSTANCE_NAME = os.getenv("EVO_INSTANCE_NAME")
AUTHENTICATION_API_KEY = os.getenv("AUTHENTICATION_API_KEY")

# ---------- WhatsApp API Class ----------
class EvolutionAPI:
    def __init__(self):
        self.base_url = EVO_BASE_URL
        self.instance_name = EVO_INSTANCE_NAME
        self.api_key = AUTHENTICATION_API_KEY
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }

    def send_message(self, number, text):
        url = f"{self.base_url}/message/sendText/{self.instance_name}"
        payload = {'number': number, 'text': text}
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

# ---------- Streamlit Page Configuration ----------
st.set_page_config(page_title="📨 Smart Message Sender", page_icon="💬", layout="centered")

# ---------- Elegant Custom Design ----------
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #e3f2fd, #e8f5e9);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333333;
        }
        .stButton>button {
            background-color: #2196F3;
            color: white;
            border-radius: 10px;
            font-weight: bold;
            font-size: 16px;
            padding: 0.6rem 1.4rem;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1976D2;
            transform: scale(1.05);
        }
        .stTextInput, .stTextArea, .stSelectbox, .stMultiselect {
            border-radius: 8px !important;
        }
        footer {
            text-align: center;
            color: #777;
            margin-top: 3rem;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- Title Section ----------
st.markdown("""
<div style='background: linear-gradient(to right, #64b5f6, #81c784); 
            border-radius: 15px; padding: 1rem; text-align:center; margin-bottom: 1rem;'>
    <h1 style='color:white; font-weight:bold;'>📨 Smart Email / WhatsApp Sender</h1>
    <h4 style='color:white;'>Send professional messages easily 🌿</h4>
</div>
""", unsafe_allow_html=True)

# ---------- Load Data ----------
try:
    receivers_df = pd.read_csv('emails.csv')
    senders_df = pd.read_csv('senders-emails.csv')
    st.success(f"✅ Receivers loaded: **{len(receivers_df)}** | Senders loaded: **{len(senders_df)}**")
except Exception as e:
    st.error(f"❌ Error loading local CSV files: {e}")
    st.stop()

# ---------- Stats Info Boxes ----------
col1, col2 = st.columns(2)
col1.metric("📧 Total Receivers", len(receivers_df))
col2.metric("📤 Total Senders", len(senders_df))

# ---------- Sending Method ----------

method = st.radio("Choose Sending Method:", ["Email", "WhatsApp"], horizontal=True)

# ---------- Message Input ----------

if method == "Email":
    subject = st.text_input("📌 Email Subject", "Test Email")
    body_template = st.text_area("💌 Email Body", "Hello {name},\nThis is a test email from my project!")
else:
    subject = None
    body_template = st.text_area("💬 WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")

# ---------- Department Filter ----------
if "dept" in receivers_df.columns:
    
    with st.expander("🏢 Departments Filter (Optional)"):
        departments = sorted(receivers_df["dept"].dropna().unique().tolist())
        selected_depts = st.multiselect("Select Department(s):", options=departments, default=departments)
        if not selected_depts:
            st.warning("⚠️ No department selected, sending to all.")
            filtered_df = receivers_df
        else:
            filtered_df = receivers_df[receivers_df["dept"].isin(selected_depts)]
            st.info(f"📋 {len(filtered_df)} receiver(s) found in selected department(s).")
else:
    st.error("❌ 'dept' column not found in your receivers CSV!")
    filtered_df = receivers_df

# ---------- WhatsApp Numbers Validation ----------
if method == "WhatsApp":
    if "number" not in filtered_df.columns:
        st.error("❌ 'number' column not found in receivers file!")
        st.stop()

# ---------- Ready to Send Section ----------

st.markdown("""
<div style='background-color:#f3e5f5; border-radius:10px; padding:1rem;'>
    🎯 Press the button below to start sending messages to the filtered receivers.
</div>
""", unsafe_allow_html=True)

if st.button(f"✨ Send {method} Messages"):
    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))
    api = EvolutionAPI()

    progress_bar = st.progress(0)
    status_text = st.empty()

    for index, row in filtered_df.iterrows():
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

                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                server.login(sender_email, app_password)
                server.send_message(msg)
                server.quit()
                status_text.success(f"✅ Email sent to {receiver} from {sender_email}")

            else:
                number = str(row["number"])
                api.send_message(number, message)
                status_text.success(f"✅ WhatsApp message sent to {number}")

            sent_count += 1
            

        except Exception as e:
            status_text.error(f"❌ Failed for {name}: {e}")

        time.sleep(2)  # Delay between messages

    
    st.success(f"🎉 All done! {sent_count}/{total} messages sent successfully.")
هاي المود وين اضيفها
