

import smtplib
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
from itertools import cycle
import requests
from io import StringIO
import os

# ---------- Page Config ----------
st.set_page_config(page_title="📧 Email / WhatsApp Sender", page_icon="📨", layout="centered")

# ---------- Custom Style ----------
st.markdown("""
    <style>
        .main { background-color: #f9f9fb; padding: 2rem; border-radius: 15px; }
        h1 { color: #4B8BBE; text-align: center; font-family: 'Helvetica Neue', sans-serif; }
        .stButton > button { background-color: #4B8BBE; color: white; border-radius: 10px; font-weight: bold; padding: 0.6rem 1.2rem; transition: 0.3s; }
        .stButton > button:hover { background-color: #357ABD; }
    </style>
""", unsafe_allow_html=True)

# ---------- Title ----------
st.title("📨 Email / WhatsApp Sender App")
st.markdown("### Send messages using multiple accounts!")

st.markdown("---")

# ---------- Load CSVs ----------
def load_csv(filename, secret_key):
    """Load CSV from local file if exists, else from Streamlit Secrets"""
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        st.info(f"Loaded {filename} from local CSV")
    else:
        csv_text = st.secrets[secret_key]
        df = pd.read_csv(StringIO(csv_text))
        st.info(f"Loaded {filename} from Secrets")
    return df

receivers_df = load_csv("emails.csv", "emails_csv")
senders_df = load_csv("senders-emails.csv", "senders_csv")

st.success(f"✅ Receivers loaded: {len(receivers_df)} | Senders loaded: {len(senders_df)}")

# ---------- Sending Method ----------
method = st.selectbox("📤 Choose Sending Method", ["Email", "WhatsApp"])

# ---------- Hidden delay variable ----------
delay = 2  # hidden from UI but still used internally

# ---------- Message Fields ----------
if method == "Email":
    subject = st.text_input("📌 Email Subject", "Test Email")
    body_template = st.text_area("💌 Email Body", "Hello {name},\nThis is a test email from my project!")
else:
    subject = None
    body_template = st.text_area("💬 WhatsApp Message", "Hi {name}, this is a test WhatsApp message!")

# ---------- Department Filter ----------
if "dept" in receivers_df.columns:
    departments = sorted(receivers_df["dept"].dropna().unique().tolist())
    selected_depts = st.multiselect("🏢 Choose Department(s)", options=departments, default=departments)
    filtered_df = receivers_df[receivers_df["dept"].isin(selected_depts)] if selected_depts else receivers_df
else:
    filtered_df = receivers_df

# ---------- WhatsApp numbers variable ----------
if method == "WhatsApp" and "number" not in filtered_df.columns:
    st.error("❌ 'number' column not found in receivers file!")
    st.stop()
elif method == "WhatsApp":
    whatsapp_numbers = filtered_df["number"].tolist()

# ---------- Ready to Send ----------
st.markdown("---")
st.subheader("🚀 Ready to Send")

if st.button(f"Send {method} Messages Now"):
    total = len(filtered_df)
    sent_count = 0
    senders_cycle = cycle(senders_df.to_dict(orient="records"))

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
                st.success(f"✅ Email sent to {receiver} from {sender_email}")

            else:  # WhatsApp
                number = str(row["number"])
                # مثال API WhatsApp
                api_base = st.secrets.get("EVO_BASE_URL")
                instance_name = st.secrets.get("EVO_INSTANCE_NAME")
                api_key = st.secrets.get("AUTHENTICATION_API_KEY")
                headers = {"apikey": api_key, "Content-Type": "application/json"}
                payload = {"number": number, "text": message}
                res = requests.post(f"{api_base}/message/sendText/{instance_name}", headers=headers, json=payload)
                st.success(f"✅ WhatsApp message sent to {number}")

            sent_count += 1
        except Exception as e:
            st.error(f"❌ Failed for {name}: {e}")

        time.sleep(delay)

    st.success(f"🎉 All done! {sent_count}/{total} messages sent successfully.")

